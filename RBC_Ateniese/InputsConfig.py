import random

class InputsConfig:

    """ Select the model to be simulated.
    0 : The base model
    1 : Bitcoin model
    2 : Ethereum model
    """
    # ----------------------------------------------------------------------------------
    model = 1
    # -----------------------------------------------------------------------------------

    # ----------------------------
    # Baseline Model (No Redactions)
    # ----------------------------
    # if model == 0:
    #     ''' --- Block Parameters --- '''
    #     Binterval = 600  # Avg. block creation time (seconds)
    #     Bsize = 1.0  # Block size (MB)
    #     Bdelay = 0.42  # Avg. block propagation delay (seconds)
    #     Breward = 12.5  # Reward for mining a block
    #
    #     ''' --- Transaction Parameters --- '''
    #     enable_transactions = True  # Enable/disable transactions in simulation
    #     transaction_model_type = "Light"  # "Full" or "Light" transaction modeling
    #     transaction_rate = 5  # Transactions generated per second
    #     Tdelay = 5.1  # Propagation delay (only for "Full" model)
    #     Tfee = 0.000062  # Avg. transaction fee
    #     Tsize = 0.0006  # Avg. transaction size (MB) (0.000546)
    #
    #     ''' --- Node Parameters --- '''
    #     total_nodes = 1000  # Total number of nodes in network
    #     miner_fraction = 0.3  # Fraction of nodes that are miners
    #     MAX_HASH_POWER = 200  # Max hash power for a miner
    #     nodes = []  # List of node objects
    #
    #     from Models.Bitcoin.Node import Node
    #     num_miners = int(total_nodes * miner_fraction)
    #
    #     # Create miner nodes
    #     for node_id in range(num_miners):
    #         hash_power = random.randint(1, MAX_HASH_POWER)
    #         nodes.append(Node(id=node_id, hashPower=hash_power))
    #
    #     # Create regular (non-mining) nodes
    #     for node_id in range(num_miners, total_nodes):
    #         nodes.append(Node(id=node_id, hashPower=0))
    #
    #
    #     ''' --- Simulation Parameters --- '''
    #     simulation_duration = 1000  # Simulation length (seconds)
    #     simulation_runs = 1         # Number of simulation runs

    # ----------------------------
    # Bitcoin Model Configuration
    # ----------------------------
    if model == 1:
        ''' --- Block Parameters --- '''
        Binterval = 600  # Avg. block creation time (seconds)
        Bsize = 1.0      # Block size (MB)
        Bdelay = 0.42    # Avg. block propagation delay (seconds) #Ref: https://bitslog.wordpress.com/2016/04/28/uncle-mining-an-ethereum-consensus-protocol-flaw/
        Breward = 12.5   # Reward for mining a block
        Rreward = 0.03   # Reward for redacting a transaction

        ''' --- Transaction Parameters --- '''
        enable_transactions = True          # Enable/disable transactions in simulation
        transaction_model_type = "Light"    # "Full" or "Light" transaction modeling
        transaction_rate = 5                # Transactions generated per second
        Tdelay = 5.1                        # Propagation delay (only for "Full" model)
        Tfee = 0.001                        # Avg. transaction fee
        Tsize = 0.0006                      # Avg. transaction size (MB)

        ''' --- Node Parameters --- '''
        total_nodes = 1000        # Total number of nodes in network
        miner_fraction = 0.3      # Fraction of nodes that are miners (Example: 0.5 ==> 50% of miners)
        nodes = []                # List of node objects
        MAX_HASH_POWER = 200      # Max hash power for a miner

        from Models.Bitcoin.Node import Node
        num_miners = int(total_nodes * miner_fraction)

        # Create miner nodes
        for node_id in range(num_miners):
            hash_power = random.randint(1, MAX_HASH_POWER)
            nodes.append(Node(id=node_id, hashPower=hash_power))

        # Create regular (non-mining) nodes
        for node_id in range(num_miners, total_nodes):
            nodes.append(Node(id=node_id, hashPower=0))

        ''' Redaction Parameters'''
        enable_redaction = True              # Enable redaction feature
        enable_multi_party = False # Enable multi-party redaction
        redaction_attempts = 1               # Number of redaction operations
        # admin_node_id = random.randint(0, len(nodes)-1)  # Node acting as admin
        admin_node_id = 10

        ''' --- Simulation Parameters --- '''
        simulation_duration = 50000  # Simulation length (seconds)
        simulation_runs = 1  # Number of simulation runs