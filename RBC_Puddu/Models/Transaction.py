import random
import string
import json
from cryptography.fernet import Fernet

from Statistics import Statistics
from InputsConfig import InputsConfig as p
import Models.Network as Network
import operator
import copy

from Models.MuTransaction import MuTransaction
from Models.Policy import Policy


class Transaction(object):
    """ Defines the Ethereum Block model.

    :param int id: the uinque id or the hash of the transaction
    :param int timestamp: the time when the transaction is created. In case of Full technique, this will be array of two value (transaction creation time and receiving time)
    :param int sender: the id of the node that created and sent the transaction
    :param int to: the id of the recipint node
    :param int value: the amount of cryptocurrencies to be sent to the recipint node
    :param int size: the transaction size in MB
    :param int gasLimit: the maximum amount of gas units the transaction can use. It is specified by the submitter of the transaction
    :param int usedGas: the amount of gas used by the transaction after its execution on the EVM
    :param int gasPrice: the amount of cryptocurrencies (in Gwei) the submitter of the transaction is willing to pay per gas unit
    :param float fee: the fee of the transaction (usedGas * gasPrice)
    """

    def __init__(self,
                 id=0,
                 timestamp=0 or [],
                 sender=0,
                 to=0,
                 value=0,
                 size=0.000546,
                 fee=0,
                 cipher = None
                 ):
        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.to = to
        self.value = value
        self.size = size
        self.fee = 0
        self.tx_set = []
        self.encrypted = True
        self._cipher = cipher




class LightTransaction():
    pending_transactions = []  # shared pool of pending transactions

    def create_nope_tx():
        nope = Transaction()
        nope.id = 0 #random.randrange(100000000000)
        nope.value = "nope"
        nope.sender=None
        nope.to=None
        return nope

    def create_mutable_tx():
        tx_set = MuTransaction()
        tx_set.transactions+=[LightTransaction.create_nope_tx()]     # Add the nope transaction
        # All the versions have the same sender and recipient
        tx_set.sender = random.choice(p.nodes).id
        tx_set.receiver = random.choice(p.nodes).id
        tx_number = random.randint(1,2)     # number of transaction in the set
        while (tx_number >0):
            # assign values for transactions' attributes. You can ignore some attributes if not of an interest, and the default values will then be used
            # key = Fernet.generate_key()
            # cipher = Fernet(key)
            tx = Transaction()
            tx.id = random.randrange(100000000000)
            tx.size = random.expovariate(1 / p.Tsize)
            tx.fee = random.expovariate(1 / p.Tfee)
            tx.value = ''.join(random.sample(string.ascii_letters, 15))
            # generate key and encrypt tx.value
            #  cipher = Fernet(key)
            # encValue = cipher.encrypt(tx.value.encode())
            # tx.value = encValue  # add transaction and decryption key to list accessed by miners
            tx_set.transactions += [tx]    # add transaction to transaction set
            tx_set.size += tx.size  # update the transactions set size
            tx_number -= 1
        tx_set.active = random.choice([tx for tx in tx_set.transactions if tx.id!=0]).id
        policy = Policy()
        policy.mutators.append(tx_set.sender)  #  add policy attributes
        tx_set.policy = policy
        tx_set.size += policy.size
        return tx_set

    def create_transactions():
        LightTransaction.pending_transactions = []
        pool = LightTransaction.pending_transactions
        Psize = int(p.transaction_rate * p.Binterval)  # Pool_size (The nbr of tx to be created per s / time (in s) creating a block)
        for i in range(Psize):
            pool += [LightTransaction.create_mutable_tx()]    #add tx_set instead of tx
        random.shuffle(pool)

    def extend(self, ref_to_tx):
        ext_list = []
        ext_size = 0
        sender = random.choice(p.nodes).id
        receiver = random.choice(p.nodes).id
        # create "tx_number" transactions and adds it to the extension list
        tx_number = random.randint(1, 3)  # number of transaction in the set
        while (tx_number > 0):
            tx = Transaction()
            tx.id = random.randrange(100000000000)
            tx.sender = sender
            tx.to = receiver
            tx.size = random.expovariate(1 / p.Tsize)
            tx.fee = random.expovariate(1 / p.Tfee)
            tx.value = ''.join(random.sample(string.ascii_letters, 15))
            ext_size += tx.size
            ext_list.append(tx)
            tx_number -= 1
        # Return the reference to transaction and the extension list of transactions
        return ref_to_tx, ext_list

    ##### Select and execute a number of transactions to be added in the next block #####
    def execute_transactions(bDepth):
        transactions_sets = []  # prepare a list of transactions to be included in the block
        size = 0  # calculate the total block gaslimit
        count = 0
        blocksize = p.Bsize
        for tx_set in LightTransaction.pending_transactions:
            Statistics.txsToBlockMap.update({tx_set: [bDepth]})
        pool = LightTransaction.pending_transactions
        pool = sorted(pool, key=lambda x: x.fee,
                      reverse=True)  # sort pending transactions in the pool based on the gasPrice value

        while count < len(pool):
            if blocksize >= pool[count].size:
                blocksize -= pool[count].size
                transactions_sets += [pool[count]]
                size += pool[count].size
            count += 1
        return transactions_sets, size


class FullTransaction():

    def create_transactions():
        Psize = int(p.transaction_rate * p.simulation_duration)

        for i in range(Psize):
            # assign values for transactions' attributes. You can ignore some attributes if not of an interest, and the default values will then be used
            tx = Transaction()

            tx.id = random.randrange(100000000000)
            creation_time = random.randint(0, p.simulation_duration - 1)
            receive_time = creation_time
            tx.timestamp = [creation_time, receive_time]
            sender = random.choice(p.nodes)
            tx.sender = sender.id
            tx.to = random.choice(p.nodes).id
            tx.size = random.expovariate(1 / p.Tsize)
            tx.fee = random.expovariate(1 / p.Tfee)

            sender.transactionsPool.append(tx)
            FullTransaction.transaction_prop(tx)

    # Transaction propogation & preparing pending lists for miners
    def transaction_prop(tx):
        # Fill each pending list. This is for transaction propagation
        for i in p.nodes:
            if tx.sender != i.id:
                t = copy.deepcopy(tx)
                t.timestamp[1] = t.timestamp[1] + Network.tx_prop_delay()  # transaction propogation delay in seconds
                i.transactionsPool.append(t)

    def execute_transactions(miner, currentTime):
        transactions = []  # prepare a list of transactions to be included in the block
        size = 0  # calculate the total block gaslimit
        count = 0
        blocksize = p.Bsize
        miner.transactionsPool.sort(key=operator.attrgetter('fee'), reverse=True)
        pool = miner.transactionsPool

        while count < len(pool):
            if blocksize >= pool[count].size and pool[count].timestamp[1] <= currentTime:
                blocksize -= pool[count].size
                transactions += [pool[count]]
                size += pool[count].size
            count += 1

        return transactions, size
