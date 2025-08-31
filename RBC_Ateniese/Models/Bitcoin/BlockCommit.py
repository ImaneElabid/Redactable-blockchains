import hashlib
import json
import random
import time
import CH.ChameleonHash as ch
import CH.SecretSharing as ss

from CH.ChameleonHash import q, g, SK, PK, KeyGen, forge, forgeSplit, chameleonHash, chameleonHashSplit
from InputsConfig import InputsConfig as p
from Models.Bitcoin.Consensus import Consensus as c
from Models.BlockCommit import BlockCommit as BaseBlockCommit
from Models.Network import Network
from Models.Transaction import LightTransaction as LT, FullTransaction as FT
from Scheduler import Scheduler
from Statistics import Statistics

SKlist = []
PKlist = []
shares = []
rlist = []

class BlockCommit(BaseBlockCommit):
    # Handling and running Events
    def handle_event(event):
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Block Creation Event
    def generate_block(event):
        startB = time.perf_counter()
        miner = p.nodes[event.block.miner]
        minerId = miner.id
        eventTime = event.time
        blockPrev = event.block.previous
        if blockPrev == miner.last_block().id:
            Statistics.totalBlocks += 1  # count # of total blocks created!

            if p.enable_transactions:
                if p.transaction_model_type == "Light":
                    blockTrans, blockSize = LT.execute_transactions()  #Get the created block (transactions and block size)
                    Statistics.blocksSize =blockSize
                elif p.transaction_model_type == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)

                event.block.transactions = blockTrans
                event.block.size = blockSize
                event.block.usedgas = blockSize

                # hash the transactions and previous hash value
                if p.enable_redaction:
                    x = json.dumps([[i.id for i in event.block.transactions], event.block.previous],
                                   sort_keys=True).encode()
                    m = hashlib.sha256(x).hexdigest()
                    if p.enable_multi_party:
                        event.block.r = [random.randint(1, q) for _ in range(len(p.nodes))]
                        event.block.id = chameleonHashSplit(PKlist, g, m, event.block.r, len(p.nodes))
                    else:
                        event.block.r = random.randint(1, q)
                        event.block.id = chameleonHash(miner.PK, m, event.block.r)

                    # event.block.id = chameleonHash(miner.PK, m, event.block.r)
            miner.blockchain.append(event.block)

            if p.enable_transactions and p.transaction_model_type == "Light":
                LT.create_transactions()  # generate transactions

            BlockCommit.propagate_block(event.block)
            endB = time.perf_counter()
            latency = endB - startB
            # Statistics.block_creation_times.append((latency))
            # print(f"[Block Created] ID: {event.block.id} | Creation Time: {latency:.6f} seconds")
            BlockCommit.generate_next_block(miner, eventTime)  # Start mining or working on the next block

    # Block Receiving Event
    def receive_block(event):
        miner = p.nodes[event.block.miner]
        minerId = miner.id
        currentTime = event.time
        blockPrev = event.block.previous  # previous block id
        node = p.nodes[event.node]  # recipient
        lastBlockId = node.last_block().id  # the id of last block

        #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block)  # append the block to local blockchain
            if p.enable_transactions and p.transaction_model_type == "Full":
                BlockCommit.update_transactionsPool(node, event.block)
            BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

        #### case 2: the received block is not built on top of the last block ####
        else:
            depth = event.block.depth + 1
            if depth > len(node.blockchain):
                BlockCommit.update_local_blockchain(node, miner, depth)
                BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

            if p.enable_transactions and p.transaction_model_type == "Full":
                BlockCommit.update_transactionsPool(node, event.block)  # not sure yet.


    # Upon generating or receiving a block, the miner start working on the next block as in POW
    def generate_next_block(node, currentTime):
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)  # time when miner x generate the next block
            Scheduler.create_block_event(node, blockTime)

    def generate_initial_events():
        currentTime = 0
        for node in p.nodes:
            BlockCommit.generate_next_block(node, currentTime)

    def propagate_block(block):
        for recipient in p.nodes:
            if recipient.id != block.miner:
                blockDelay = Network.block_prop_delay()
                # draw block propagation delay from a distribution !! or assign 0 to ignore block propagation delay
                Scheduler.receive_block_event(recipient, block, blockDelay)

    def setupSecretSharing():
        global SKlist, PKlist, rlist, shares
        SKlist, PKlist = KeyGen(ch.p, q, g, len(p.nodes))
        rlist = ch.getr(len(p.nodes), q)
        for i, node in enumerate(p.nodes):
            node.PK = PKlist[i]
            node.SK = SKlist[i]

    def generate_redaction_event(redactRuns):
        t1 = time.time()
        i = 0
        miner_list = [node for node in p.nodes if node.hashPower > 0]
        while i < redactRuns:
            if p.enable_multi_party:
                miner = random.choice(miner_list)
            else:
                miner = p.nodes[p.admin_node_id]
            r = random.randint(1, 2)
            # r =2
            block_index = random.randint(1, len(miner.blockchain)-1)
            tx_index = random.randint(1, len(miner.blockchain[block_index].transactions)-1)
            if r == 1:
                BlockCommit.redact_tx(miner, block_index, tx_index, p.Tfee)
            else:
                BlockCommit.delete_tx(miner, block_index, tx_index)
            i += 1
        t2 = time.time()
        total_redaction_time = (t2 - t1) * 1000  # in ms
        print(f"Total redaction operations time = {total_redaction_time:.2f} ms")

    def delete_tx(miner, i, tx_i):
        t1 = time.time()
        block = miner.blockchain[i]
        # Store the old block data
        x1 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        m1 = hashlib.sha256(x1).hexdigest()

        # record the block index and deleted transaction object, miner reward  = 0 and performance time = 0
        # and also the blockchain size, number of transaction of that action block
        # removed_tx = block.transactions.pop(tx_i)
        miner.redacted_tx.append([i, block.transactions.pop(tx_i), 0, 0, miner.blockchain_length(), len(block.transactions)])

        # Store the modified block data
        x2 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        m2 = hashlib.sha256(x2).hexdigest()
        # Forge new r
        if p.enable_multi_party:
            # block.r should be a list of randomness values for multi-party
            rlist = block.r
            miner_list = [node for node in p.nodes if node.hashPower > 0]
            # propagation delay in sharing secret key
            # time.sleep(0.005)
            ss.secret_share(SK, minimum=len(miner_list), shares=len(p.nodes))
            r2 = ch.forgeSplit(SKlist, m1, rlist, m2, q, miner.id)
            rlist[miner.id] = r2
            block.r = rlist
            # Compute new block id using chameleonHashSplit
            block.id = ch.chameleonHashSplit(PKlist, g, m2, rlist, len(p.nodes))
            # propagate change to other nodes
            for node in p.nodes:
                if node.id != miner.id:
                    if node.blockchain[i]:
                        node.blockchain[i].transactions = block.transactions
                        node.blockchain[i].r = block.r
        else:
            # Centralized setting
            r2 = ch.forge(SK, m1, block.r, m2)
            block.r = r2
            block.id = ch.chameleonHash(PK, m2, r2)
        # Calculate the performance time per operation
        t2 = time.time()
        t = (t2 - t1) * 1000 # in ms
        # redact operation is more expensive than mining
        # print(f"Redaction succeeded in {t}")
        reward = random.expovariate(1 / p.Rreward)
        miner.balance += reward
        miner.redacted_tx[-1][2] = reward
        miner.redacted_tx[-1][3] = t
        return miner

    def redact_tx(miner, i, tx_i, fee):
        t1 = time.time()
        block = miner.blockchain[i]
        # Store the old block data
        x1 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        m1 = hashlib.sha256(x1).hexdigest()

        # record the block depth and modify transaction information then recompute the transaction id
        block.transactions[tx_i].fee = fee
        block.transactions[tx_i].id = random.randrange(100000000000)
        # record the block depth, redacted transaction, miner reward = 0 and performance time = 0
        miner.redacted_tx.append([i, block.transactions[tx_i], 0, 0, miner.blockchain_length(), len(block.transactions)])

        # Store the modified block data
        x2 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        m2 = hashlib.sha256(x2).hexdigest()
        # Forge new r
        # t1 = time.time()
        if p.enable_multi_party:
            rlist = block.r
            r2 = ch.forgeSplit([node.SK for node in p.nodes], m1, rlist, m2, ch.q, miner.id)
            rlist[miner.id] = r2
            block.r = rlist
            block.id = ch.chameleonHashSplit([node.PK for node in p.nodes], ch.g, m2, rlist, len(p.nodes))
            # propagate change to other nodes
            for node in p.nodes:
                if node.id != miner.id:
                    if node.blockchain[i]:
                        node.blockchain[i].transactions = block.transactions.copy()
                        node.blockchain[i].r = block.r.copy()
        else:
            r2 = ch.forge(ch.SK, m1, block.r, m2)
            block.r = r2
            block.id = ch.chameleonHash(PK, m2, r2)
        # Calculate the performance time per operation
        t2 = time.time()
        t = (t2 - t1) * 1000 # in ms
        block.redaction_time =t
        # print(f"Redaction succeeded in {t}")
        # redact operation is more expensive than mining
        reward = random.expovariate(1 / p.Rreward)
        miner.balance += reward
        miner.redacted_tx[-1][2] = reward
        miner.redacted_tx[-1][3] = t
        return miner
