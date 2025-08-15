import copy
import logging
import os
import random
import time

from Event import Event
from InputsConfig import InputsConfig as p
from Models.Bitcoin.Consensus import Consensus as c
from Models.Block import Block
from Models.BlockCommit import BlockCommit as BaseBlockCommit
from Models.MuTransaction import MuTransaction
from Models.Network import Network
from Models.Transaction import LightTransaction as LT, FullTransaction as FT, Transaction

from Scheduler import Scheduler
from Statistics import Statistics

from cryptography.fernet import Fernet

class BlockCommit(BaseBlockCommit):
    # Handling and running Events
    def handle_event(event):
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Block Creation Event
    def generate_block(event: Event):
        miner = p.nodes[event.block.miner]
        eventTime = event.time
        blockPrev = event.block.prev_block

        if blockPrev.id == miner.last_block().id:  # I am up-to-date and can start mining the block
            Statistics.totalBlocks += 1  # count # of total blocks created!
            if p.enable_transactions:
                if p.transaction_model_type == "Light":
                    blockTrans, blockSize = LT.execute_transactions(event.block.depth)  # Get the created block (transactions and block size)
                    Statistics.blocksSize = blockSize
                    event.block.transactions = blockTrans
                    event.block.size = blockSize
                elif p.transaction_model_type == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)
                    event.block.transactions = blockTrans
                    event.block.size = blockSize

                # hash the transactions and previous hash value
                if p.enable_redaction:
                    BlockCommit.mutate(event.block)

            miner.blockchain.append(event.block)

            if p.enable_transactions and p.transaction_model_type == "Light":
                LT.create_transactions()  # generate new transactions

            BlockCommit.propagate_block(event.block)
            BlockCommit.generate_next_block(miner, eventTime)  # Start mining or working on the next block

    # Block Receiving Event
    def receive_block(event):
        miner = p.nodes[event.block.miner]
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

        if Statistics.totalBlocks >= 3:
            if p.redactions > 0:  # propose redact "redactions" times
                if node in p.Proposers:
                     # select randomly when to mutate
                    if random.choice([True, False]):
                        Statistics.redact_st = time.time()
                        BlockCommit.propose_mutant(node)
                        p.redactions -= 1

    # Upon generating or receiving a block, the miner start working on the next block as in POW
    def generate_next_block(node, currentTime):
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)  # time when miner x generate the next block
            Scheduler.create_block_event(node, blockTime)

    def generate_initial_events():
        currentTime = 0
        for node in p.nodes:
            BlockCommit.generate_next_block(node, currentTime)

    def propagate_block(block: Block):
        for recipient in p.nodes:
            if recipient.id != block.miner:
                blockDelay = Network.block_prop_delay()
                # draw block propagation delay from a distribution !! or you can assign 0 to ignore block propagation delay
                Scheduler.receive_block_event(recipient, block, blockDelay)

    def get_keys(miner, id):  # only miners get the enc/dec keys
        for node in p.nodes:
            if node.id == miner and node.hashPower > 0:
                return id._cipher
        else:
            raise ValueError(f"A regular uses trying to access the keys is {miner}")

    def get_tx_by_id(id, tx_list):
        return [i for i in tx_list if i.id == id]

    def mutate(block):
        if len(Statistics.pending_mutation) > 0:        # if there is some mutation proposals
            for mutator in Statistics.pending_mutation.keys():   # {proposer: [ref_T,active]}
                ref_T, new_active = Statistics.pending_mutation.get(mutator)[0], Statistics.pending_mutation.get(mutator)[1]
                if BlockCommit.policy_check(mutator, ref_T , new_active):
                    # print(f"current block {block.depth} ... mutation was in block={Statistics.txsToBlockMap.get(ref_T)}")
                    # if new_active != 0:
                    tx = BlockCommit.get_tx_by_id(new_active, ref_T.transactions)[0]
                    #     print(tx.value)
                    #     cipher = BlockCommit.get_keys(block.miner, tx)
                    #     decrypted = cipher.decrypt(tx.value).decode()
                    #     print(decrypted)
                    mutation = MuTransaction(id=ref_T, active=new_active)
                    block.transactions.append(mutation)
                    block.size += p.Tsize

                    #  TODO add entry in block and update block size
                    Statistics.redact_et = time.time()
                    t = (Statistics.redact_et - Statistics.redact_st) * 1000
                    print(f">>>> MUTATION SUCCEEDED!! in {t}  <<<<")
                    miner = [node for node in p.nodes if node.id == block.miner][0]
                    reward = random.expovariate(1 / p.Rreward)
                    miner.balance += reward
                    miner.redacted_tx.append(
                        [Statistics.txsToBlockMap.get(ref_T)[0], tx, reward, t, miner.blockchain_length(), len(block.transactions)])
                    if len(miner.redacted_tx) != 0:
                        miner.redacted_tx[-1][2] = reward
                        miner.redacted_tx[-1][3] = t
                    Statistics.txsToBlockMap[ref_T].append(block)
                else:
                    print("**MUTATION FAILED**")
            Statistics.pending_mutation.pop(mutator)  # remove block from pending redactions
        #  TODO delete keys of old active/ send keys of new_active

    def propose_mutant(node):  # node, i, tx_i
        ref_T = random.choice(list(Statistics.txsToBlockMap.keys())) # choose which tx_set we mutate
        block_index= Statistics.txsToBlockMap.get(ref_T) # get all the blocks that contain related transactions

        if len(block_index)==1:    # if has only one block, get active transaction id
            old=ref_T.active
            new_active = random.choice([tx for tx in ref_T.transactions]).id
        else:
            # TODO to check in case of multiple mutation!!!!
            all_tx=[]        # gather all transactions related to ref_T
            for index in block_index:
                for set in node.blockchain[index].transactions:
                    if set.id == ref_T.id:
                        all_tx.append(set.transactions)
            new_active = random.choice(all_tx)  # empty !!!!!!
        Statistics.pending_mutation.update({node.id:[ref_T,new_active]})     # proposer: [ref_T,active]

    def policy_check(node, ref_T , new_active):
        # verify  new_active != old_active && policy.mutator == proposer && policy.time <= current_time
        if ref_T.active != new_active:
            if node in ref_T.policy.mutators:
                if ref_T.policy.time > time.time():
                    # print(f"Mutation verified for txSet: {ref_T.id}")
                    return True
                else:
                    print(f"***FAILED: redaction period exceeded!!!")
            else:
                print(f"***FAILED: Illegible mutator!!")
        else:
            print(f"***FAILED: Active version is same!!!")
            return False

