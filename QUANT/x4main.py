#!/usr/bin/env python
import requests
import argparse
import sys
import csv 
import math
import re
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
    parser.add_argument("-f", "--funda", help="Analyse - F:Fundamentals")
    args   = parser.parse_args()

    # Update the catalog
    if args.catalog:
        refresh_catalog()

    # Get the list of stocks
    catalog     = x4fns.read_csv(EQCatalog)
    stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
        
    # Fundamental Analysis
    if args.funda:
        header  = ['STOCK']
        header.extend(['1Y_S_U', '1Y_S_L',
                       '2Y_S_U', '2Y_S_L'
                      ])
        header.extend(['1Y_P_U', '1Y_P_L',
                       '2Y_P_U', '2Y_P_L'
                      ])
        funda   = [header]

    for stock in stocks:

        print ("Processing for stock: "+stock['symbol'])
        if args.leech:
            # Leech technical information (price / volume)
            if 'H' in args.leech:
                tech_leech(stock['symbol'], 'H')
            if 'D' in args.leech:
                tech_leech(stock['symbol'], 'D')
            if 'W' in args.leech:
                tech_leech(stock['symbol'], 'W')
            # Leech fundamental information (sales, profit etc.)
            if 'F' in args.leech:
                funda_leech(stock['symbol'], 'C', 'F')

        if args.funda:
            tech_data   = x4fns.readall_csv(HISTDIR+stock['symbol']+CSV)[-1]
            ltp         = '{0:.2f}'.format(float(tech_data[PHIST['CLOSE']]))
            row         = [stock['symbol']]
            if 'S' in stock['ratios']:
                s_ru_1y, s_rl_1y = evaluate_bands(stock['symbol'], 'SALES', 252)
                s_ru_2y, s_rl_2y = evaluate_bands(stock['symbol'], 'SALES', 504)
                trow = [s_ru_1y, s_rl_1y, s_ru_2y, s_rl_2y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            elif 'I' in stock['ratios']:
                i_ru_1y, i_rl_1y = evaluate_bands(stock['symbol'], 'INCOME', 252)
                i_ru_2y, i_rl_2y = evaluate_bands(stock['symbol'], 'INCOME', 504)
                trow = [i_ru_1y, i_rl_1y, i_ru_2y, i_rl_2y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            else:
                row.extend([0, 0, 0, 0])

            if 'O' in stock['ratios']:
                o_ru_1y, o_rl_1y = evaluate_bands(stock['symbol'], 'OPP', 252)
                o_ru_2y, o_rl_2y = evaluate_bands(stock['symbol'], 'OPP', 504)
                trow = [o_ru_1y, o_rl_1y, o_ru_2y, o_rl_2y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            elif 'P' in stock['ratios']:
                p_ru_1y, p_rl_1y = evaluate_bands(stock['symbol'], 'PAT', 252)
                p_ru_2y, p_rl_2y = evaluate_bands(stock['symbol'], 'PAT', 504)
                trow = [p_ru_1y, p_rl_1y, p_ru_2y, p_rl_2y]
                row.extend([int(x) if isinstance(x, float) else x for x in trow])
            else:
                row.extend([0, 0, 0, 0])
            funda.append(row)

    if args.funda:
        x4fns.write_csv(DBDIR+'Fundamental_Analysis'+CSV, funda, 'w')
        update_ranges(funda)
