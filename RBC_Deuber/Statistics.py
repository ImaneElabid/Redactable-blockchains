import time

from InputsConfig import InputsConfig as p
from Models.Consensus import Consensus as c
from Models.Incentives import Incentives
import pandas as pd
import os
from openpyxl import load_workbook


class Statistics:
    # Global variables used to calculate and print stimulation results
    redacted_tx = []
    totalBlocks = 0
    mainBlocks = 0
    staleBlocks = 0
    staleRate = 0
    blockData = []
    blocksResults = []
    blocksSize = []
    profits = [[0 for x in range(7)] for y in
               range(p.simulation_runs * len(p.nodes))]  # rows number of miners * number of runs, columns =7
    index = 0
    original_chain = []
    chain = []
    redactResults = []
    allRedactRuns = []
    pending_redactions = []
    candidate_pool = []  # contain validated blocks that need to be voted on
    voting_list = {}
    redact_st = 0
    redact_et = 0
    voting_start = 0
    voting_end = 0
    redaction_time_st = 0
    redaction_time_et = 0
    VT = 0

    # Timing metrics
    simulation_start_time = 0
    simulation_end_time = 0
    total_execution_time = 0
    block_creation_times = []
    redaction_times = []
    average_block_time = 0
    average_redaction_time = 0
    total_block_creation_time = 0
    total_redaction_time = 0

    def calculate(t):
        Statistics.total_execution_time = t
        Statistics.global_chain()  # print the global chain
        Statistics.blocks_results(
            t)  # calculate and print block statistics e.g., # of accepted blocks and stale rate etc
        Statistics.profit_results(t)  # calculate and distribute the revenue or reward for miners
        if p.enable_redaction:
            Statistics.redact_result()  # to calculate the info per redact operation
        Statistics.calculate_timing_metrics()  # calculate timing statistics

    # Calculate block statistics Results
    def blocks_results(t):
        trans = 0
        Statistics.mainBlocks = len(c.global_chain) - 1
        Statistics.staleBlocks = Statistics.totalBlocks - Statistics.mainBlocks
        for b in c.global_chain:
            trans += len(b.transactions)
        Statistics.staleRate = round(Statistics.staleBlocks / Statistics.totalBlocks * 100, 2)
        Statistics.blockData = [Statistics.totalBlocks, Statistics.mainBlocks, Statistics.staleBlocks,
                                Statistics.staleRate, trans, t, str(Statistics.blocksSize)]
        Statistics.blocksResults += [Statistics.blockData]

    ############################ Calculate and distibute rewards among the miners #############################
    def profit_results(self):

        for m in p.nodes:
            i = Statistics.index + m.id * p.simulation_runs
            Statistics.profits[i][0] = m.id
            Statistics.profits[i][1] = m.hashPower
            Statistics.profits[i][2] = m.blocks
            Statistics.profits[i][3] = round(m.blocks / Statistics.mainBlocks * 100, 2)
            Statistics.profits[i][4] = 0
            Statistics.profits[i][5] = 0
            Statistics.profits[i][6] = m.balance
        # print("Profits :")
        # print(Statistics.profits)

        Statistics.index += 1

    ########################################################### prepare the global chain  ###########################################################################################
    def global_chain():
        print(f">>>> Actual redaction time = {Statistics.VT} ms")
        for i in c.global_chain:
            block = [i.depth, i.id, i.previous, i.timestamp, i.miner, len(i.transactions), i.size]
            Statistics.chain += [block]
        print("Length of GLOBAL CHAIN = " + str(len(Statistics.chain)))
        # print(Statistics.chain)

    def original_global_chain():
        for i in c.global_chain:
            block = [i.depth, i.id, i.previous, i.timestamp, i.miner, len(i.transactions), str(i.size)]
            Statistics.original_chain += [block]

    ########################################################## generate redaction data ############################################################
    def redact_result():
        i = 0
        profit_count, op_count = 0, p.redaction_attempts
        while i < len(p.nodes):
            if p.redaction_attempts == 0:
                profit_count = 0
            if len(p.nodes[i].redacted_tx) != 0 and p.redaction_attempts > 0:
                for j in range(len(p.nodes[i].redacted_tx)):
                    print(
                        f'Deletion/Redaction: Block Depth => {p.nodes[i].redacted_tx[j][0]}, Transaction ID => {p.nodes[i].redacted_tx[j][1].id}')
                    # Added Miner ID,Block Depth,Transaction ID,Redaction Profit,Performance Time (ms),Blockchain Length,# of Tx
                    result = [p.nodes[i].id, p.nodes[i].redacted_tx[j][0], p.nodes[i].redacted_tx[j][1].id,
                              p.nodes[i].redacted_tx[j][2], p.nodes[i].redacted_tx[j][3],
                              p.nodes[i].redacted_tx[j][4], p.nodes[i].redacted_tx[j][5]]
                    profit_count += p.nodes[i].redacted_tx[j][2]
                    Statistics.redactResults.append(result)
            i += 1
        Statistics.allRedactRuns.append([profit_count, op_count])

    ########################################################## Calculate timing metrics ############################################################
    def calculate_timing_metrics():
        """Calculate comprehensive timing statistics"""
        # Calculate block creation timing metrics
        if Statistics.block_creation_times:
            Statistics.total_block_creation_time = sum(Statistics.block_creation_times)
            Statistics.average_block_time = Statistics.total_block_creation_time / len(Statistics.block_creation_times)

        # Calculate redaction timing metrics
        if Statistics.redaction_times:
            Statistics.total_redaction_time = sum(Statistics.redaction_times)
            Statistics.average_redaction_time = Statistics.total_redaction_time / len(Statistics.redaction_times)

    ########################################################### Print simulation results to Excel ###########################################################################################
    def print_to_excel(fname):

        df1 = pd.DataFrame(
            {'Block Time': [p.Binterval], 'Block Propagation Delay': [p.Bdelay], 'No. Miners': [len(p.nodes)],
             'Simulation Time': [p.simulation_duration]})
        # data = {'Stale Rate': Results.staleRate,'# Stale Blocks': Results.staleBlocks,'# Total Blocks': Results.totalBlocks, '# Included Blocks': Results.mainBlocks}

        df2 = pd.DataFrame(Statistics.blocksResults)
        df2.columns = ['Total Blocks', 'Main Blocks', 'Stale Blocks', 'Stale Rate',
                       '# transactions', 'Performance Time', 'Block sizeeeeeee']

        df3 = pd.DataFrame(Statistics.profits)
        df3.columns = ['Miner ID', '% Hash Power', '# Mined Blocks', '% of main blocks', '# Uncle Blocks',
                       '% of uncles', 'Profit (in ETH)']

        df4 = pd.DataFrame(Statistics.chain)
        print(df4)
        # df4.columns= ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions','Block Size']
        df4.columns = ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions',
                       'Block Size']

        # Timing metrics dataframe
        timing_data = {
            'Total Execution Time (ms)': [Statistics.total_execution_time],
            'Total Block Creation Time (ms)': [Statistics.total_block_creation_time],
            'Average Block Creation Time (ms)': [Statistics.average_block_time],
            'Total Redaction Time (ms)': [Statistics.total_redaction_time],
            'Average Redaction Time (ms)': [Statistics.average_redaction_time],
            'Block Creation Count': [len(Statistics.block_creation_times)],
            'Redaction Count': [len(Statistics.redaction_times)],
            'Block Throughput (blocks/sec)': [Statistics.mainBlocks / (
                        Statistics.total_execution_time / 1000) if Statistics.total_execution_time > 0 else 0],
            'Transaction Throughput (tx/sec)': [sum(len(block.transactions) for block in c.global_chain) / (
                        Statistics.total_execution_time / 1000) if Statistics.total_execution_time > 0 else 0],
            'Redaction Throughput (redactions/sec)': [len(Statistics.redaction_times) / (
                        Statistics.total_execution_time / 1000) if Statistics.total_execution_time > 0 and Statistics.redaction_times else 0]
        }
        df_timing = pd.DataFrame(timing_data)

        if p.enable_redaction:
            if p.redaction_attempts > 0:
                # blockchain history before redaction
                df7 = pd.DataFrame(Statistics.original_chain)
                # df4.columns= ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions','Block Size']
                df7.columns = ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID',
                               '# transactions',
                               'Block Size']

                # Redaction results
                df5 = pd.DataFrame(Statistics.redactResults)
                print(df5)
                df5.columns = ['Miner ID', 'Block Depth', 'Transaction ID', 'Redaction Profit', 'Performance Time (ms)',
                               'Blockchain Length', '# of Tx']

            df6 = pd.DataFrame(Statistics.allRedactRuns)
            print(df6)
            df6.columns = ['Total Profit/Cost', 'Redact op runs']
        writer = pd.ExcelWriter(fname, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='InputConfig')
        df2.to_excel(writer, sheet_name='SimOutput')
        df3.to_excel(writer, sheet_name='Profit')
        df_timing.to_excel(writer, sheet_name='TimingMetrics')

        if p.enable_redaction and p.redaction_attempts > 0:
            df2.to_csv('Results/time_redact.csv', sep=',', mode='a+', index=False, header=True)
            df7.to_excel(writer, sheet_name='ChainBeforeRedaction')
            df5.to_excel(writer, sheet_name='RedactResult')
            df4.to_excel(writer, sheet_name='Chain')
            # Add the result to transaction/performance time csv to statistic analysis
            df5.to_csv('Results/tx_time.csv', sep=',', mode='a+', index=False, header=True)
            # Add the result to block length/performance time csv to statistic analysis, and fixed the number of transactions
            df5.to_csv('Results/block_time.csv', sep=',', mode='a+', index=False, header=True)
            # if p.hasMulti:
            # df5.to_csv('Results/block_time_den.csv', sep=',', mode='a+', index=False, header=True)
            # df5.to_csv('Results/tx_time_den.csv', sep=',', mode='a+', index=False, header=True)
            # Add the total profit earned vs the number of redaction operation runs
            df6.to_csv('Results/profit_redactRuns.csv', sep=',', mode='a+', index=False, header=True)
        else:
            df4.to_excel(writer, sheet_name='Chain')
            df2.to_csv('Results/time.csv', sep=',', mode='a+', index=False, header=True)
        writer.close()

    ########################################################### Display comprehensive metrics ###########################################################################################
    def display_metrics():
        """Display all available metrics for assessment"""
        print("\n" + "=" * 80)
        print("RBC_DEUBER BLOCKCHAIN SIMULATION METRICS")
        print("=" * 80)

        # Basic Blockchain Metrics
        print("\n📊 BLOCKCHAIN PERFORMANCE METRICS:")
        print(f"  • Total Blocks Created: {Statistics.totalBlocks}")
        print(f"  • Main Chain Blocks: {Statistics.mainBlocks}")
        print(f"  • Stale Blocks: {Statistics.staleBlocks}")
        print(f"  • Stale Rate: {Statistics.staleRate}%")
        print(f"  • Chain Length: {len(Statistics.chain)}")

        # Transaction Metrics
        total_transactions = sum(len(block.transactions) for block in c.global_chain)
        avg_tx_per_block = total_transactions / len(c.global_chain) if len(c.global_chain) > 0 else 0
        print(f"  • Total Transactions: {total_transactions}")
        print(f"  • Average Transactions per Block: {avg_tx_per_block:.2f}")

        # Network Metrics
        total_miners = sum(1 for node in p.nodes if node.hashPower > 0)
        total_nodes = len(p.nodes)
        print(f"\n🌐 NETWORK METRICS:")
        print(f"  • Total Nodes: {total_nodes}")
        print(f"  • Mining Nodes: {total_miners}")
        print(f"  • Non-mining Nodes: {total_nodes - total_miners}")
        print(f"  • Mining Participation Rate: {(total_miners / total_nodes) * 100:.2f}%")

        # Hash Power Distribution
        total_hash_power = sum(node.hashPower for node in p.nodes)
        if total_hash_power > 0:
            print(f"  • Total Network Hash Power: {total_hash_power}")
            max_hash_power = max(node.hashPower for node in p.nodes)
            print(f"  • Maximum Single Node Hash Power: {max_hash_power}")
            print(f"  • Hash Power Concentration: {(max_hash_power / total_hash_power) * 100:.2f}%")

        # Mining Rewards and Economics
        total_rewards = sum(node.balance for node in p.nodes)
        print(f"\n💰 ECONOMIC METRICS:")
        print(f"  • Total Rewards Distributed: {total_rewards:.6f} ETH")
        print(
            f"  • Average Reward per Miner: {total_rewards / total_miners:.6f} ETH" if total_miners > 0 else "  • Average Reward per Miner: 0 ETH")

        # Top miners by blocks mined
        miners_by_blocks = [(node.id, node.blocks, node.balance) for node in p.nodes if node.hashPower > 0]
        miners_by_blocks.sort(key=lambda x: x[1], reverse=True)
        print(f"  • Top 5 Miners by Blocks Mined:")
        for i, (miner_id, blocks, balance) in enumerate(miners_by_blocks[:5]):
            print(f"    {i + 1}. Miner {miner_id}: {blocks} blocks, {balance:.6f} ETH")

        # Redaction Metrics (if enabled)
        if p.enable_redaction:
            print(f"\n🔄 REDACTION METRICS (VOTING-BASED):")
            print(f"  • Redaction Enabled: Yes")
            print(f"  • Redaction Attempts: {p.redaction_attempts}")
            print(f"  • Vote Period: {p.VotePeriod} blocks")
            print(f"  • Vote Threshold (RHO): {p.RHO}")

            total_redactions = len(Statistics.redactResults)
            total_redaction_profit = sum(result[3] for result in Statistics.redactResults)
            avg_redaction_time = sum(
                result[4] for result in Statistics.redactResults) / total_redactions if total_redactions > 0 else 0

            print(f"  • Total Successful Redactions: {total_redactions}")
            print(f"  • Total Redaction Profit: {total_redaction_profit:.6f} ETH")
            print(f"  • Average Redaction Time: {avg_redaction_time:.2f} ms")
            print(f"  • Voting Time: {Statistics.VT:.2f} ms")

            if total_redactions > 0:
                redaction_by_miner = {}
                for result in Statistics.redactResults:
                    miner_id = result[0]
                    if miner_id not in redaction_by_miner:
                        redaction_by_miner[miner_id] = {'count': 0, 'profit': 0}
                    redaction_by_miner[miner_id]['count'] += 1
                    redaction_by_miner[miner_id]['profit'] += result[3]

                print(f"  • Redactions by Miner:")
                for miner_id, data in redaction_by_miner.items():
                    print(f"    - Miner {miner_id}: {data['count']} redactions, {data['profit']:.6f} ETH profit")
        else:
            print(f"\n🔄 REDACTION METRICS:")
            print(f"  • Redaction Enabled: No")

        # Configuration Metrics
        print(f"\n⚙️  CONFIGURATION METRICS:")
        print(f"  • Block Interval: {p.Binterval} seconds")
        print(f"  • Block Size: {p.Bsize} MB")
        print(f"  • Block Propagation Delay: {p.Bdelay} seconds")
        print(f"  • Block Reward: {p.Breward} ETH")
        if p.enable_redaction:
            print(f"  • Redaction Reward: {p.Rreward} ETH")
        print(f"  • Transaction Rate: {p.transaction_rate} tx/second")
        print(f"  • Transaction Fee: {p.Tfee} ETH")
        print(f"  • Transaction Size: {p.Tsize} MB")
        print(f"  • Simulation Duration: {p.simulation_duration} seconds")

        # Timing Performance Metrics
        print(f"\n⏱️  TIMING PERFORMANCE METRICS:")
        print(f"  • Total Execution Time: {Statistics.total_execution_time:.2f} ms")

        if Statistics.block_creation_times:
            Statistics.total_block_creation_time = sum(Statistics.block_creation_times)
            Statistics.average_block_time = Statistics.total_block_creation_time / len(Statistics.block_creation_times)
            print(f"  • Total Block Creation Time: {Statistics.total_block_creation_time:.2f} ms")
            print(f"  • Average Block Creation Time: {Statistics.average_block_time:.2f} ms")
            print(f"  • Fastest Block Creation: {min(Statistics.block_creation_times):.2f} ms")
            print(f"  • Slowest Block Creation: {max(Statistics.block_creation_times):.2f} ms")
            print(
                f"  • Block Creation Efficiency: {(Statistics.total_block_creation_time / Statistics.total_execution_time) * 100:.2f}%")
        else:
            print(f"  • Block Creation Times: No data available")

        if Statistics.redaction_times:
            Statistics.total_redaction_time = sum(Statistics.redaction_times)
            Statistics.average_redaction_time = Statistics.total_redaction_time / len(Statistics.redaction_times)
            print(f"  • Total Redaction Time: {Statistics.total_redaction_time:.2f} ms")
            print(f"  • Average Redaction Time: {Statistics.average_redaction_time:.2f} ms")
            print(f"  • Fastest Redaction: {min(Statistics.redaction_times):.2f} ms")
            print(f"  • Slowest Redaction: {max(Statistics.redaction_times):.2f} ms")
            print(
                f"  • Redaction Efficiency: {(Statistics.total_redaction_time / Statistics.total_execution_time) * 100:.2f}%")

            # Redaction vs Block Creation Performance Comparison
            if Statistics.block_creation_times:
                redaction_vs_block_ratio = Statistics.average_redaction_time / Statistics.average_block_time
                print(f"  • Redaction vs Block Creation Ratio: {redaction_vs_block_ratio:.2f}x")
        else:
            print(f"  • Redaction Times: No data available")

        # Throughput Metrics
        if Statistics.total_execution_time > 0:
            blocks_per_second = (Statistics.mainBlocks / (Statistics.total_execution_time / 1000))
            print(f"  • Block Throughput: {blocks_per_second:.2f} blocks/second")

            total_transactions = sum(len(block.transactions) for block in c.global_chain)
            tx_per_second = total_transactions / (Statistics.total_execution_time / 1000)
            print(f"  • Transaction Throughput: {tx_per_second:.2f} tx/second")

            if Statistics.redaction_times:
                redactions_per_second = len(Statistics.redaction_times) / (Statistics.total_execution_time / 1000)
                print(f"  • Redaction Throughput: {redactions_per_second:.2f} redactions/second")

        # Network Efficiency Metrics
        print(f"\n📈 NETWORK EFFICIENCY METRICS:")
        if Statistics.total_execution_time > 0:
            simulation_time_seconds = Statistics.total_execution_time / 1000
            print(f"  • Simulation Duration: {simulation_time_seconds:.2f} seconds")
            print(f"  • Average Block Time: {p.Binterval} seconds (configured)")
            if Statistics.mainBlocks > 0:
                actual_avg_block_time = simulation_time_seconds / Statistics.mainBlocks
                print(f"  • Actual Average Block Time: {actual_avg_block_time:.2f} seconds")
                efficiency = (p.Binterval / actual_avg_block_time) * 100
                print(f"  • Block Time Efficiency: {efficiency:.2f}%")

        # Memory and Storage Metrics
        total_blockchain_size = sum(block.size for block in c.global_chain)
        avg_block_size = total_blockchain_size / len(c.global_chain) if len(c.global_chain) > 0 else 0
        print(f"\n💾 STORAGE METRICS:")
        print(f"  • Total Blockchain Size: {total_blockchain_size:.6f} MB")
        print(f"  • Average Block Size: {avg_block_size:.6f} MB")
        print(f"  • Configured Block Size: {p.Bsize} MB")

        # Transaction Metrics Detail
        if len(c.global_chain) > 0:
            total_transactions = sum(len(block.transactions) for block in c.global_chain)
            avg_tx_per_block = total_transactions / len(c.global_chain)
            total_tx_fees = sum(sum(tx.fee for tx in block.transactions) for block in c.global_chain)
            avg_tx_fee = total_tx_fees / total_transactions if total_transactions > 0 else 0

            print(f"\n💳 DETAILED TRANSACTION METRICS:")
            print(f"  • Total Transactions: {total_transactions}")
            print(f"  • Average Transactions per Block: {avg_tx_per_block:.2f}")
            print(f"  • Total Transaction Fees: {total_tx_fees:.6f} ETH")
            print(f"  • Average Transaction Fee: {avg_tx_fee:.6f} ETH")
            print(f"  • Configured Transaction Rate: {p.transaction_rate} tx/second")

        # Security Metrics
        print(f"\n🔒 SECURITY METRICS:")
        if hasattr(p, 'admin_node_id'):
            print(f"  • Admin Node ID: {p.admin_node_id}")

        # Voting-specific metrics
        if p.enable_redaction:
            print(f"  • Voting Parameters:")
            print(f"    - Vote Period: {p.VotePeriod} blocks")
            print(f"    - Vote Threshold (RHO): {p.RHO}")
            print(f"    - Pending Redactions: {len(Statistics.pending_redactions)}")
            print(f"    - Candidate Pool Size: {len(Statistics.candidate_pool)}")
            print(f"    - Active Voting Sessions: {len(Statistics.voting_list)}")

        print("\n" + "=" * 80)

    ########################################################### Reset all global variables used to calculate the simulation results ###########################################################################################
    def reset():
        Statistics.totalBlocks = 0
        Statistics.mainBlocks = 0
        Statistics.staleBlocks = 0
        Statistics.staleRate = 0
        Statistics.blockData = []

    def reset2():
        Statistics.blocksResults = []
        Statistics.profits = [[0 for x in range(7)] for y in
                              range(p.simulation_runs * len(
                                  p.nodes))]  # rows number of miners * number of runs, columns =7
        Statistics.index = 0
        Statistics.chain = []
        Statistics.redactResults = []
        Statistics.allRedactRuns = []
        Statistics.block_creation_times = []
        Statistics.redaction_times = []
        Statistics.total_block_creation_time = 0
        Statistics.total_redaction_time = 0
        Statistics.average_block_time = 0
        Statistics.average_redaction_time = 0
