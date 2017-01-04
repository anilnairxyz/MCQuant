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

# Parameters 

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Batch Job to run all")
    parser.add_argument("-s", "--stock", help="name of stock")
    parser.add_argument("-l", "--leech", help="Leech H: Historic, F:Fundamental")
    parser.add_argument("-f", "--funda", help="Analyse Fundamentals")
#    parser.add_argument("window", help="duration in trading days", type=int)
#    parser.add_argument("value", help="Value for testing - 'S':Sales, 'I':Income, 'O':Op profit, 'P':PAT")
    args   = parser.parse_args()
    if args.stock:
        stocks = [args.stock]
    else:
        # Read the source file which contains all the details on the stocks
        catalog = x4fns.read_csv(EQCatalog)
        stocks  = [x[PCAT['NSECODE']] for x in catalog]
        
    if args.funda:
        funda   = [['STOCK', '6M_INC_BB', '6M_INC_RB', \
                             '6M_PAT_BB', '6M_PAT_RB', \
                             '1Y_INC_BB', '1Y_INC_RB', \
                             '1Y_PAT_BB', '1Y_PAT_RB', \
                             '2Y_INC_BB', '2Y_INC_RB', \
                             '2Y_PAT_BB', '2Y_PAT_RB' \
                             ]]
    for stock in stocks:

        print ("Processing for stock: "+stock)
        if args.leech:
            # Leech technical information (price / volume)
            if 'H' in args.leech:
                tech_leech('H', stock)
            if 'D' in args.leech:
                tech_leech('D', stock)
            if 'W' in args.leech:
                tech_leech('W', stock)
            # Leech fundamental information (sales, profit etc.)
            if 'F' in args.leech:
                funda_leech(stock, 'C', 'F')

        if args.funda:
            inc_bb_6m = bollinger_bands(stock, 'INCOME', 126)
            inc_rb_6m = range_bands(stock, 'INCOME', 126)
            pat_bb_6m = bollinger_bands(stock, 'PAT', 126)
            pat_rb_6m = range_bands(stock, 'PAT', 126)
            inc_bb_1y = bollinger_bands(stock, 'INCOME', 252)
            inc_rb_1y = range_bands(stock, 'INCOME', 252)
            pat_bb_1y = bollinger_bands(stock, 'PAT', 252)
            pat_rb_1y = range_bands(stock, 'PAT', 252)
            inc_bb_2y = bollinger_bands(stock, 'INCOME', 504)
            inc_rb_2y = range_bands(stock, 'INCOME', 504)
            pat_bb_2y = bollinger_bands(stock, 'PAT', 504)
            pat_rb_2y = range_bands(stock, 'PAT', 504)
            funda.append([stock,
                          inc_bb_6m,inc_rb_6m,pat_bb_6m,
                          pat_rb_6m,inc_bb_1y,inc_rb_1y,
                          pat_bb_1y,pat_rb_1y,inc_bb_2y,
                          inc_rb_2y,pat_bb_2y,pat_rb_2y])

    if args.funda:
        x4fns.write_csv(DBDIR+'Fundamental_Analysis'+CSV, funda, 'w')
