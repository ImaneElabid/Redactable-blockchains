import time

from InputsConfig import InputsConfig as p
from Models.Consensus import Consensus as c
from Models.Incentives import Incentives
import pandas as pd
import numpy as np
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
    pending_mutation = {}       # {proposer: [ref_T,active]}
    txsToBlockMap = {}      # {tx_set: [blocks.depth]}
    decryption_keys = {}
    redact_st = 0
    redact_et = 0
    tx_summary = {}     # {ref_T.id: all txs of the corresponding transaction set}

    def calculate(t):
        Statistics.global_chain()  # print the global chain
        Statistics.blocks_results(t)  # calculate and print block statistics e.g., # of accepted blocks and stale rate etc
        #  Statistics.profit_results(t)  # calculate and distribute the revenue or reward for miners
        if p.enable_redaction:
            Statistics.redact_result()  # to calculate the info per redact operation

    # Calculate block statistics Results
    def blocks_results(t):
        trans = 0
        Statistics.mainBlocks = len(c.global_chain) - 1
        Statistics.staleBlocks = Statistics.totalBlocks - Statistics.mainBlocks
        for b in c.global_chain:
            trans += len(b.transactions)
        Statistics.staleRate = round(Statistics.staleBlocks / Statistics.totalBlocks * 100, 2)
        Statistics.blockData = [Statistics.totalBlocks, Statistics.mainBlocks, Statistics.staleBlocks, Statistics.staleRate, trans, t, str(Statistics.blocksSize)]
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
        #print("Profits :")
        #print(Statistics.profits)

        Statistics.index += 1

    ########################################################### prepare the global chain  ###########################################################################################
    def global_chain():
        for i in c.global_chain:
            block = [i.depth, i.id, i.previous, i.timestamp, i.miner, len(i.transactions), i.size]
            Statistics.chain += [block]
        print("==========THE GLOBAL CHAIN========== of length = "+str(len(Statistics.chain)))
        #print(Statistics.chain)


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
                    # print(f'Deletion/Redaction: Block Depth => {p.NODES[i].redacted_tx[j][0]}, Transaction ID => {p.NODES[i].redacted_tx[j][1].id}')
                    # Added Miner ID,Block Depth,Transaction ID,Redaction Profit,Performance Time (ms),Blockchain Length,# of Tx
                    result = [p.nodes[i].id, p.nodes[i].redacted_tx[j][0], p.nodes[i].redacted_tx[j][1].id,
                              p.nodes[i].redacted_tx[j][2], p.nodes[i].redacted_tx[j][3],
                              p.nodes[i].redacted_tx[j][4], p.nodes[i].redacted_tx[j][5]]
                    profit_count += p.nodes[i].redacted_tx[j][2]
                    Statistics.redactResults.append(result)
            i += 1
        Statistics.allRedactRuns.append([profit_count, op_count])

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
                #df5.columns = ['Miner ID', 'Block Depth', 'Transaction ID', 'Redaction Profit', 'Performance Time (ms)', 'Blockchain Length', '# of Tx']

            df6 = pd.DataFrame(Statistics.allRedactRuns)
            print(df6)
            df6.columns = ['Total Profit/Cost', 'Redact op runs']
        writer = pd.ExcelWriter(fname, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='InputConfig')
        df2.to_excel(writer, sheet_name='SimOutput')
        df3.to_excel(writer, sheet_name='Profit')
        if p.enable_redaction and p.redaction_attempts > 0:
            # df2.to_csv('Results/time_redact.csv', sep=',', mode='a+', index=False, header=False)
            df7.to_excel(writer, sheet_name='ChainBeforeRedaction')
            df5.to_excel(writer, sheet_name='RedactResult')
            df4.to_excel(writer, sheet_name='Chain')
            # Add the result to transaction/performance time csv to statistic analysis
            # df5.to_csv('Results_new/tx_time.csv', sep=',', mode='a+', index=False, header=False)
            # Add the result to block length/performance time csv to statistic analysis, and fixed the number of transactions
            # df5.to_csv('Results/block_time.csv', sep=',', mode='a+', index=False, header=False)
            # if p.hasMulti:
                # df5.to_csv('Results/block_time_den.csv', sep=',', mode='a+', index=False, header=False)
                # df5.to_csv('Results/tx_time_den.csv', sep=',', mode='a+', index=False, header=False)
            # Add the total profit earned vs the number of redaction operation runs
            # df6.to_csv('Results/profit_redactRuns.csv', sep=',', mode='a+', index=False, header=False)
        else:
            df4.to_excel(writer, sheet_name='Chain')
            # df2.to_csv('Results_new/time.csv', sep=',', mode='a+', index=False, header=False)
        writer.close()


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
                              range(p.simulation_runs * len(p.nodes))]  # rows number of miners * number of runs, columns =7
        Statistics.index = 0
        Statistics.chain = []
        Statistics.redactResults = []
        Statistics.allRedactRuns = []
