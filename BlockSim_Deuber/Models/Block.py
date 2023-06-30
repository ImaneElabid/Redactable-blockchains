import hashlib
import json

from Models.Utils import get_hash, compute_hash


class Block(object):
    """ Defines the base Block model.

    :param int depth: the index of the block in the local blockchain ledger (0 for genesis block)
    :param int id: the uinque id or the hash of the block
    :param int previous: the uinque id or the hash of the previous block
    :param int timestamp: the time when the block is created
    :param int miner: the id of the miner who created the block
    :param list transactions: a list of transactions included in the block
    :param int size: the block size in MB
    :param int PrevHash: the previous hash << S >>
    :param int state: the initial state of the block << y >>
    :param int r: the randomness value to implement chameleon hash function
    """

    def __init__(self,
                 depth=0,
                 id=0,
                 previous=-1,
                 prev_block=None,
                 timestamp=0,
                 miner=None,
                 transactions=[],
                 size=1.0,
                 prev_hash="0",
                 block_state=compute_hash(["0", []]),
                 edited_tx=None
                 ):
        self.depth = depth
        self.id = id
        self.previous = previous
        self.prev_block = prev_block
        self.timestamp = timestamp
        self.miner = miner
        self.transactions = transactions or []
        self.size = size
        self.prev_hash = prev_hash
        self.block_state = block_state
        self.edited_tx = edited_tx
