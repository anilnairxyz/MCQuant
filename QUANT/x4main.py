#!/usr/bin/env python
import requests
import argparse
import sys
import csv 
import math
import re
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from dateutil import parser
from x4defs import *
import x4fns
from tech_leech import *
from funda_leech import *
from funda_anal import *
from x4gsheet import *

# Parameters 

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Batch Job to run all")
    parser.add_argument("-u", "--catalog", help="Update - C:Catalog")
    parser.add_argument("-l", "--leech", help="Leech H: Historic, F:Fundamental")
    parser.add_argument("-a", "--analyse", help="Analyse - F:Fundamentals, C:Nifty")
    args   = parser.parse_args()

    # Define the threading worker
    class LeechWorker(Thread):
       def __init__(self, queue):
           Thread.__init__(self)
           self.queue = queue
    
       def run(self):
           while True:
               # Get the work from the queue and expand the tuple
               symbol, mode = self.queue.get()
               if mode == 'F':
                   funda_leech(symbol, 'C', 'F')
               else:
                   tech_leech(symbol, mode)
               self.queue.task_done()


    # Update the catalog
    if args.catalog:
        refresh_catalog()

    # Get the list of stocks
    catalog     = x4fns.read_csv(EQCatalog)
    stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
        
    # Fundamental Analysis
    if args.analyse:
        if 'F' in args.analyse:
            f_anal = True
        else:
            f_anal = False

        if 'C' in args.analyse:
            cf_anal = True
        else:
            cf_anal = False
    else:
        f_anal = False
        cf_anal = False

    if f_anal:
        header  = ['STOCK']
        header.extend(['6M_S_U', '6M_S_L',
                       '1Y_S_U', '1Y_S_L',
                       '2Y_S_U', '2Y_S_L',
                       '4Y_S_U', '4Y_S_L'
                      ])
        header.extend(['6M_P_U', '6M_P_L',
                       '1Y_P_U', '1Y_P_L',
                       '2Y_P_U', '2Y_P_L',
                       '4Y_P_U', '4Y_P_L'
                      ])
        header.extend(['Sales', 'OPP'])
        funda   = [header]


    if args.leech:
        queue = Queue()
        # Create 8 worker threads
        for x in range(8):
            worker = LeechWorker(queue)
            # Setting True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        # Leech technical information (price / volume)
        if 'H' in args.leech:
            for symbol in [stock['symbol'] for stock in stocks]+['NIFTY']:
                print ("Leeching technical for stock: "+symbol)
                queue.put((symbol, 'H'))
            queue.join()
        if 'D' in args.leech:
            for symbol in [stock['symbol'] for stock in stocks]+['NIFTY']:
                print ("Leeching technical for stock: "+symbol)
                queue.put((symbol, 'D'))
            queue.join()
        if 'W' in args.leech:
            for symbol in [stock['symbol'] for stock in stocks]+['NIFTY']:
                print ("Leeching technical for stock: "+symbol)
                queue.put((symbol, 'W'))
            queue.join()

        # Leech fundamental information (sales, profit etc.)
        if 'F' in args.leech:
            for stock in stocks:
                print ("Leeching fundamental for stock: "+stock['symbol'])
                queue.put((stock['symbol'], 'F'))
            queue.join()

    if f_anal:
        for stock in stocks:
            print ("Fundamental Analysis for stock: "+stock['symbol'])
            tech_data   = x4fns.readall_csv(HISTDIR+stock['symbol']+CSV)[-1]
            ltp         = '{0:.2f}'.format(float(tech_data[PHIST['CLOSE']]))
            row         = [stock['symbol']]
            if 'S' in stock['ratios']:
                s_ru_6m, s_rl_6m, sps = evaluate_bands(stock['symbol'], 'SALES', 126, mode='P')
                s_ru_1y, s_rl_1y = evaluate_bands(stock['symbol'], 'SALES', 252)
                s_ru_2y, s_rl_2y = evaluate_bands(stock['symbol'], 'SALES', 504)
                s_ru_4y, s_rl_4y = evaluate_bands(stock['symbol'], 'SALES', 1008)
                trow = [s_ru_6m, s_rl_6m, s_ru_1y, s_rl_1y, s_ru_2y, s_rl_2y, s_ru_4y, s_rl_4y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            elif 'I' in stock['ratios']:
                i_ru_6m, i_rl_6m, sps = evaluate_bands(stock['symbol'], 'INCOME', 126, mode='P')
                i_ru_1y, i_rl_1y = evaluate_bands(stock['symbol'], 'INCOME', 252)
                i_ru_2y, i_rl_2y = evaluate_bands(stock['symbol'], 'INCOME', 504)
                i_ru_4y, i_rl_4y = evaluate_bands(stock['symbol'], 'INCOME', 1008)
                trow = [i_ru_6m, i_rl_6m, i_ru_1y, i_rl_1y, i_ru_2y, i_rl_2y, i_ru_4y, i_rl_4y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            else:
                sps = None
                row.extend([0, 0, 0, 0, 0, 0, 0, 0])

            if 'O' in stock['ratios']:
                o_ru_6m, o_rl_6m, eps = evaluate_bands(stock['symbol'], 'OPP', 126, mode='P')
                o_ru_1y, o_rl_1y = evaluate_bands(stock['symbol'], 'OPP', 252)
                o_ru_2y, o_rl_2y = evaluate_bands(stock['symbol'], 'OPP', 504)
                o_ru_4y, o_rl_4y = evaluate_bands(stock['symbol'], 'OPP', 1008)
                trow = [o_ru_6m, o_rl_6m, o_ru_1y, o_rl_1y, o_ru_2y, o_rl_2y, o_ru_4y, o_rl_4y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            elif 'P' in stock['ratios']:
                p_ru_6m, p_rl_6m, eps = evaluate_bands(stock['symbol'], 'PAT', 126, mode='P')
                p_ru_1y, p_rl_1y = evaluate_bands(stock['symbol'], 'PAT', 252)
                p_ru_2y, p_rl_2y = evaluate_bands(stock['symbol'], 'PAT', 504)
                p_ru_4y, p_rl_4y = evaluate_bands(stock['symbol'], 'PAT', 1008)
                trow = [p_ru_6m, p_rl_6m, p_ru_1y, p_rl_1y, p_ru_2y, p_rl_2y, p_ru_4y, p_rl_4y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            else:
                eps = None
                row.extend([0, 0, 0, 0, 0, 0, 0, 0])
            row.extend([sps, eps])
            funda.append(row)

    if f_anal:
        x4fns.write_csv(DBDIR+'Fundamental_Analysis'+CSV, funda, 'w')
        update_ranges(funda)

    if cf_anal:
        tech_data   = x4fns.readall_csv(HISTDIR+'NIFTY'+CSV)[-1]
        ltp         = float(tech_data[PHIST['CLOSE']])
        u, l, m, s  = evaluate_bands('NIFTY', 'SALES', 1008, stat=True)
        level_4y_s  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_4y_s  = int((ltp - l)*100/(u - l))
        u, l, m, s  = evaluate_bands('NIFTY', 'SALES', 504, stat=True)
        level_2y_s  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_2y_s  = int((ltp - l)*100/(u - l))
        u, l, m, s  = evaluate_bands('NIFTY', 'SALES', 252, stat=True)
        level_1y_s  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_1y_s  = int((ltp - l)*100/(u - l))
        u, l, m, s  = evaluate_bands('NIFTY', 'PAT', 1008, stat=True)
        level_4y_p  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_4y_p  = int((ltp - l)*100/(u - l))
        u, l, m, s  = evaluate_bands('NIFTY', 'PAT', 504, stat=True)
        level_2y_p  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_2y_p  = int((ltp - l)*100/(u - l))
        u, l, m, s  = evaluate_bands('NIFTY', 'PAT', 252, stat=True)
        level_1y_p  = int(x4fns.cumnormdist((ltp - m)/s)*100)
        range_1y_p  = int((ltp - l)*100/(u - l))
        nifty       = [['','4Y_NORM','4Y_RANGE','2Y_NORM','2Y_RANGE','1Y_NORM', '1Y_RANGE']]
        nifty.append(['SALES',level_4y_s,range_4y_s,level_2y_s,range_2y_s,level_1y_s,range_1y_s])
        nifty.append(['PROFIT',level_4y_p,range_4y_p,level_2y_p,range_2y_p,level_1y_p,range_1y_p])
        update_nifty(nifty)
