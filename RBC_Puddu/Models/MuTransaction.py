import random
from Models.Policy import Policy

class MuTransaction(object):
    def __init__(self,
                 id = random.randrange(100000000000),
                 timestamp=0 or [],
                 transactions = [],
                 size=0,
                 active = None,
                 policy = None,
                 sender = None,
                 receiver =None,
                 fee=0
                 ):
        self.id = id
        self.timestamp = timestamp
        self.transactions = []
        self.size = size
        self.active = active
        self.policy = policy
        self.sender = sender
        self.receiver= receiver
        self.fee = fee

    # def create_tx_set(self, tx):
    #     tx_set = {}
    #     return tx_set
    # instead of creating a transaction the user proposes a set of transactions

    # def create_mutable_tx(self):
    #     policy = Policy()
    #     pass

    #

    # def mutate(self):
    #     pass

    #

    # def extend(self):
    #     pass
