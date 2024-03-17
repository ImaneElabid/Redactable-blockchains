import random
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
        NUM_NODES = 3  # the total number of nodes in the network
        NODES = []
        from Models.Node import Node
        # here as an example we define three nodes by assigning a unique id for each one
        NODES = [Node(id=0), Node(id=1), Node(id=2)]

        ''' Simulation Parameters '''
        simTime = 2200  # the simulation length (in seconds)
        Runs = 1  # Number of simulation runs

    ''' Input configurations for Bitcoin model '''
    if model == 1:
        ''' Block Parameters '''
        Binterval = 600  # Average time (in seconds)for creating a block in the blockchain
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
        NUM_NODES = 1000  # the total number of nodes in the network
        NODES = []
        MINERS_PORTION = 0.3  # Example: 50% of miners
        MAX_HASH_POWER = 200

        from Models.Bitcoin.Node import Node
        num_miners = int(NUM_NODES * MINERS_PORTION)

        # Create miners
        for i in range(num_miners):
            hash_power = random.randint(1, MAX_HASH_POWER)
            NODES.append(Node(id=i, hashPower=hash_power))

        # Create regular nodes
        for i in range(num_miners, NUM_NODES):
            NODES.append(Node(id=i, hashPower=0))

        Proposers = [node for node in NODES if (node.id == 0)] #or node.id ==6
        ''' Simulation Parameters '''
        simTime = 100000  # the simulation length (in seconds)
        Runs = 1  # Number of simulation runs
        VotePeriod = 100 # voting is collected over blocks
        RHO = 75  # voting is collected over blocks

        ''' Redaction Parameters'''
        hasRedact = True
        redactRuns = 1
        redactions = 1
        adminNode = random.randint(0, len(NODES))
        # adminNode = 1
