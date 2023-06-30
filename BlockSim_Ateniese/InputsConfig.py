# import random

class InputsConfig:

    """ Select the model to be simulated.
    0 : The base model
    1 : Bitcoin model
    2 : Ethereum model
    3 : AppendableBlock model
    """
    model = 1

    ''' Input configurations for the base model '''
    if model == 0:

        ''' Block Parameters '''
        Binterval = 600  # Average time (in seconds)for creating a block in the blockchain
        Bsize = 1.0  # The block size in MB
        Bdelay = 0.42  # average block propogation delay in seconds, #Ref: https://bitslog.wordpress.com/2016/04/28/uncle-mining-an-ethereum-consensus-protocol-flaw/
        Breward = 12.5  # Reward for mining a block

        ''' Transaction Parameters '''
        hasTrans = True  # True/False to enable/disable transactions in the simulator
        Ttechnique = "Light"  # Full/Light to specify the way of modelling transactions
        Tn = 10  # The rate of the number of transactions to be created per second
        # The average transaction propagation delay in seconds (Only if Full technique is used)
        Tdelay = 5.1
        Tfee = 0.000062  # The average transaction fee
        Tsize = 0.000546  # The average transaction size  in MB

        ''' Node Parameters '''
        Nn = 15  # the total number of nodes in the network
        NODES = []
        from Models.Node import Node
        # here as an example we define three nodes by assigning a unique id for each one
        NODES = [Node(id=0, hashPower=50), Node(id=1, hashPower=0), Node(id=2, hashPower=0),
                 Node(id=3, hashPower=150), Node(id=4, hashPower=50), Node(id=5, hashPower=150),
                 Node(id=6, hashPower=0), Node(id=7, hashPower=100), Node(id=8, hashPower=0),
                 Node(id=9, hashPower=0),Node(id=10, hashPower=0), Node(id=11, hashPower=0),
                 Node(id=12, hashPower=0), Node(id=13, hashPower=0), Node(id=14, hashPower=100)]

        ''' Simulation Parameters '''
        simTime = 100000  # the simulation length (in seconds)
        Runs = 1  # Number of simulation runs

    ''' Input configurations for Bitcoin model '''
    if model == 1:
        ''' Block Parameters '''
        Binterval = 400  # Average time (in seconds)for creating a block in the blockchain
        Bsize = 1.0  # The block size in MB
        Bdelay = 0.42  # average block propogation delay in seconds, #Ref: https://bitslog.wordpress.com/2016/04/28/uncle-mining-an-ethereum-consensus-protocol-flaw/
        Breward = 12.5  # Reward for mining a block
        Rreward = 0.03  # Reward for redacting a transaction

        ''' Transaction Parameters '''
        hasTrans = True  # True/False to enable/disable transactions in the simulator
        Ttechnique = "Light"  # Full/Light to specify the way of modelling transactions
        Tn = 5  # The rate of the number of transactions to be created per second
        # The average transaction propagation delay in seconds (Only if Full technique is used)
        Tdelay = 5.1
        Tfee = 0.001  # The average transaction fee
        Tsize = 0.0006  # The average transaction size in MB

        ''' Node Parameters '''
        Nn = 15 # the total number of nodes in the network
        NODES = []
        from Models.Bitcoin.Node import Node
        # here as an example we define three nodes by assigning a unique id for each one + % of hash (computing) power
        NODES = [	Node(id=0, hashPower=50), Node(id=1, hashPower=10), Node(id=2, hashPower=20),
         Node(id=3, hashPower=40), Node(id=4, hashPower=50), Node(id=5, hashPower=150),
         Node(id=6, hashPower=50), Node(id=7, hashPower=100), Node(id=8, hashPower=80),
         Node(id=9, hashPower=110), Node(id=10, hashPower=40), Node(id=11, hashPower=100),
         Node(id=12, hashPower=220), Node(id=13, hashPower=30), Node(id=14, hashPower=100),
         Node(id=15, hashPower=150),Node(id=16, hashPower=50), Node(id=17, hashPower=100),
         Node(id=18, hashPower=80),Node(id=19, hashPower=110), Node(id=20, hashPower=40),
         Node(id=21, hashPower=60), Node(id=22, hashPower=200), Node(id=23, hashPower=0),
         Node(id=24, hashPower=160), Node(id=25, hashPower=150), Node(id=26, hashPower=50),
         Node(id=27, hashPower=100), Node(id=28, hashPower=80), Node(id=29, hashPower=110),
          Node(id=30, hashPower=40),Node(id=31, hashPower=60), Node(id=32, hashPower=200),
Node(id=33, hashPower=120),Node(id=34, hashPower=160), Node(id=35, hashPower=150),
Node(id=36, hashPower=50), Node(id=37, hashPower=100), Node(id=38, hashPower=80),
Node(id=39, hashPower=110),Node(id=40, hashPower=40),Node(id=41, hashPower=60), Node(id=42, hashPower=200),
Node(id=43, hashPower=120),Node(id=44, hashPower=160), Node(id=45, hashPower=150),
Node(id=46, hashPower=50), Node(id=47, hashPower=100), Node(id=48, hashPower=80),
Node(id=49, hashPower=110),Node(id=50, hashPower=50), Node(id=51, hashPower=10), Node(id=52, hashPower=20),
         Node(id=53, hashPower=40), Node(id=54, hashPower=50), Node(id=55, hashPower=150),
         Node(id=56, hashPower=50), Node(id=57, hashPower=100), Node(id=58, hashPower=80),
         Node(id=59, hashPower=110), Node(id=60, hashPower=40), Node(id=61, hashPower=100),
         Node(id=62, hashPower=220), Node(id=63, hashPower=30), Node(id=64, hashPower=100),
         Node(id=65, hashPower=150),Node(id=66, hashPower=50), Node(id=67, hashPower=100),
         Node(id=68, hashPower=80),Node(id=69, hashPower=110), Node(id=70, hashPower=40), Node(id=71, hashPower=100),
         Node(id=72, hashPower=220), Node(id=73, hashPower=30), Node(id=74, hashPower=100),
         Node(id=75, hashPower=150),Node(id=76, hashPower=50), Node(id=77, hashPower=100),
         Node(id=78, hashPower=80),Node(id=79, hashPower=110), Node(id=80, hashPower=40), Node(id=81, hashPower=100),
         Node(id=82, hashPower=220), Node(id=83, hashPower=30), Node(id=84, hashPower=100),
         Node(id=85, hashPower=150),Node(id=86, hashPower=50), Node(id=87, hashPower=100),
         Node(id=88, hashPower=80),Node(id=89, hashPower=110)]
        ''' Simulation Parameters '''
        simTime = 100000  # the simulation length (in seconds)
        Runs = 1  # Number of simulation runs

        ''' Redaction Parameters'''
        hasRedact = True
        hasMulti = True
        redactRuns = 1
        # adminNode = random.randint(0, len(NODES))
        adminNode = 0

