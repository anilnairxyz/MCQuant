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
#    parser.add_argument("window", help="duration in trading days", type=int)
#    parser.add_argument("value", help="Value for testing - 'S':Sales, 'I':Income, 'O':Op profit, 'P':PAT")
    args   = parser.parse_args()
    if args.stock:
        stocks = [args.stock]
    else:
        # Read the source file which contains all the details on the stocks
        catalog = x4fns.read_csv(EQCatalog)
        stocks  = [x[PCAT['NSECODE']] for x in catalog]
        
    for stock in stocks:

        print ("Processing for stock: "+stock)
        if args.leech:
            # Leech technical information (price / volume)
            if 'H' in args.leech:
#                tech_leech('H', stock)
                print ("Leech Historic")
            if 'D' in args.leech:
#                tech_leech('D', stock)
                print ("Leech Daily")
            if 'W' in args.leech:
#                tech_leech('W', stock)
                print ("Leech Weekly")
            # Leech fundamental information (sales, profit etc.)
            if 'F' in args.leech:
#                funda_leech(stock, 'C', 'F')
                print ("Leech Fundamentals")

#    last_close  = close[-1]
#    last_ratio  = df['RATIO'].iloc[-1]
#    print (last_close, last_ratio)
#    x4fns.write_csv('aaa.csv', annualized, 'w')