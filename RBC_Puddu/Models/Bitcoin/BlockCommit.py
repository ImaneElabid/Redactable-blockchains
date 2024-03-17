import copy
import hashlib
import json
import random
import time

from Event import Event
from InputsConfig import InputsConfig as p
from Models.Bitcoin.Consensus import Consensus as c
from Models.Block import Block
from Models.BlockCommit import BlockCommit as BaseBlockCommit
from Models.Network import Network
from Models.Transaction import LightTransaction as LT, FullTransaction as FT, Transaction
from Models.Utils import compute_hash
from Scheduler import Scheduler
from Statistics import Statistics


class BlockCommit(BaseBlockCommit):

    # Handling and running Events
    def handle_event(event):
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Block Creation Event
    def generate_block(event: Event):
        miner = p.NODES[event.block.miner]
        eventTime = event.time
        blockPrev = event.block.prev_block

        if blockPrev.id == miner.last_block().id:  # I am up-to-date and can start mining the block
            Statistics.totalBlocks += 1  # count # of total blocks created!
            if p.hasTrans:
                if p.Ttechnique == "Light":
                    blockTrans, blockSize = LT.execute_transactions()  # Get the created block (transactions and block size)
                    Statistics.blocksSize = blockSize
                    event.block.transactions = blockTrans
                    event.block.size = blockSize
                    G = compute_hash([blockPrev.prev_hash, blockPrev.transactions])
                    event.block.prev_hash = compute_hash([G, blockPrev.block_state])
                    event.block.block_state = compute_hash([event.block.prev_hash, event.block.transactions])
                elif p.Ttechnique == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)
                    event.block.transactions = blockTrans
                    event.block.size = blockSize

                # hash the transactions and previous hash value
                if p.hasRedact:
                    t1 = time.time()
                    if len(Statistics.pending_redactions) > 0:  # if there some redaction proposals
                        for index, candidate_block in Statistics.pending_redactions:
                            if BlockCommit.validateCand(miner, index, candidate_block):
                                Statistics.voting_list.update({candidate_block.id: [p.VotePeriod,
                                                                                    0]})  # create entry in the voting list <block id: [vote_period, vote_counter]
                                BlockCommit.addVote(event, candidate_block, miner)
                                BlockCommit.evaluateVote(candidate_block)

                    if len(Statistics.candidate_pool) > 0:
                        for index, candidate_block in Statistics.candidate_pool:
                            if candidate_block.id not in miner.voted.keys():
                                BlockCommit.addVote(event, candidate_block, miner)
                            BlockCommit.evaluateVote(candidate_block)
                    t2 = time.time()
                    # Calculate the performance time per operation
                    t = (t2 - t1) * 1000  # in ms
                    reward = random.expovariate(1 / p.Rreward)
                    miner.balance += reward
                    # miner.redacted_tx[-1][2] = reward
                    # miner.redacted_tx[-1][3] = t
            miner.blockchain.append(event.block)

            if p.hasTrans and p.Ttechnique == "Light":
                LT.create_transactions()  # generate new transactions

            BlockCommit.propagate_block(event.block)
            BlockCommit.generate_next_block(miner, eventTime)  # Start mining or working on the next block

    # Block Receiving Event
    def receive_block(event):
        miner = p.NODES[event.block.miner]
        currentTime = event.time
        blockPrev = event.block.previous  # previous block id
        node = p.NODES[event.node]  # recipient
        lastBlockId = node.last_block().id  # the id of last block

        #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block)  # append the block to local blockchain
            if p.hasTrans and p.Ttechnique == "Full":
                BlockCommit.update_transactionsPool(node, event.block)
            BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

        #### case 2: the received block is not built on top of the last block ####
        else:
            depth = event.block.depth + 1
            if depth > len(node.blockchain):
                BlockCommit.update_local_blockchain(node, miner, depth)
                BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

            if p.hasTrans and p.Ttechnique == "Full":
                BlockCommit.update_transactionsPool(node, event.block)  # not sure yet.

        if Statistics.totalBlocks >= 3:
            if p.redactions > 0:  # propose redact "redactions" times
                if node in p.Proposers:
                    BlockCommit.create_candidate_block(node)
                    p.redactions -= 1

    # Upon generating or receiving a block, the miner start working on the next block as in POW
    def generate_next_block(node, currentTime):
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)  # time when miner x generate the next block
            Scheduler.create_block_event(node, blockTime)
            # print("NODE " + str(node.id) + "# is MINING (creation of a new block)....")

    def generate_initial_events():
        currentTime = 0
        for node in p.NODES:
            BlockCommit.generate_next_block(node, currentTime)

    def propagate_block(block: Block):
        for recipient in p.NODES:
            if recipient.id != block.miner:
                blockDelay = Network.block_prop_delay()
                # draw block propagation delay from a distribution !! or you can assign 0 to ignore block propagation delay
                Scheduler.receive_block_event(recipient, block, blockDelay)

    def validateCand(miner, depth, candidate: Block):
        prevBlock = miner.blockchain[depth - 1]
        nextBlock = miner.blockchain[depth + 1]

        # print(f"S2: {compute_hash([candidate.block_state, candidate.block_state])}")
        # G = compute_hash([candidate.prev_hash, candidate.transactions])
        # print(f"S2***: {compute_hash([G, candidate.block_state])}")
        # print(f"NEXT: {nextBlock.prev_hash}")

        if candidate.prev_hash == compute_hash(
                [prevBlock.block_state, prevBlock.block_state]) and nextBlock.prev_hash == compute_hash(
            [candidate.block_state, candidate.block_state]):  # check : s_j = h(y_j_1,y_j_1) and s_j+1 = h(y_j,y_j)
            print("Passed verification..")
            # todo only one miner checks the validity of the cand block !!
            Statistics.candidate_pool.append([depth, candidate])  # Add block to verified redactions
            Statistics.pending_redactions.remove([depth, candidate])  # remove block from pending redactions
            return True
        else:
            print(f"Verification of block {depth} = False")
            Statistics.pending_redactions.remove([depth, candidate])
            return False

    def create_candidate_block(node):  # node, i, tx_i
        i = random.randrange(2, Statistics.totalBlocks)
        # select the block to redact from the miner's blockchain
        candidate_block = copy.deepcopy(node.blockchain[i])
        # select transaction index among the tx in the selected block
        tx_index = random.randrange(len(candidate_block.transactions))
        tx = candidate_block.transactions[tx_index]
        tx.id = random.randrange(800000000000, 900000000000)
        tx.value = 'To-REDACT' + str(tx.id)
        Statistics.pending_redactions.append([i, candidate_block])
        candidate_block.edited_tx = tx_index
        #  TODO i need to keep track of the edited transaction (tx_index)

    def addVote(event, block, miner):
        vote = compute_hash([block.id])  # vote = the hash of the candidate block id
        vote_tx = Transaction(id=miner.id, value=vote)
        event.block.transactions.append(vote_tx)  # add vote hash to mined block transaction
        event.block.size += p.Tsize  # update the block size
        print(f"vote of :{block.id}  by  {miner.id}")
        Statistics.voting_list[block.id][1] += 1  # increment the number of votes
        miner.voted[block.id] = True

    def evaluateVote(block):  # when a new block is mined decrement the voting period and increment the number of votes
        if Statistics.voting_list[block.id][0] == 0:  # if vote period ended check policy
            BlockCommit.policy_check(block, Statistics.voting_list[block.id][1])
        else:
            Statistics.voting_list[block.id][0] -= 1  # increment the voting period timer
        # print(Statistics.voting_list)

    def policy_check(block: Block, vote_count: int):
        if vote_count >= p.RHO:  # votes >= ratio within voting period ==> ACCEPT
            print("Redaction succeeded")
            # record the block depth, redacted transaction, miner reward = 0 and performance time = 0
            miner = [node for node in p.NODES if node.id == block.miner][0]
            Statistics.redacted_tx.append(
                [block.depth, block.transactions[block.edited_tx], 0, 0, miner.blockchain_length(),
                 len(block.transactions)])
            Statistics.candidate_pool.remove([block.depth, block])
            return True
        else:  # votes < ratio within voting period ==> REJECT
            Statistics.candidate_pool.remove([block.depth, block])
            print("REDACTION REJECTED")
            # start a second round
            return False

