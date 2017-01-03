#!/usr/bin/env python
import requests
import argparse
import sys
import csv 
import math
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

def tech_leech(mode, stock):

    # Read the source file which contains all the details on the stocks
    catalog = x4fns.read_csv(EQCatalog)

    if mode == 'H':
        mc_url = HISTURL
        output_dir = HISTDIR
    elif mode == 'W':
        mc_url = WEEKURL
        output_dir = WEEKDIR
    else:
        mc_url = DAYURL
        output_dir = DAYDIR
    
    if stock != 'NIFTY':
        catrow = [x for x in catalog if x[PCAT['NSECODE']]==stock][0]
        mc_code = catrow[PCAT['MCCODE']]
    else:
        mc_code = 'nifty'
    url = mc_url+mc_code+'.csv'
    
    # fetch the data
    response = requests.get(url)
    html = response.content
    #create the output file
    output_file = open(output_dir+stock+CSV, "w+")
    #write to the respective files
    html = html.decode('utf-8')
    output_file.write(html)
    output_file.close()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser("Leech Stock Prices from MC")
    parser.add_argument("stock", help="name of stock")
    parser.add_argument("mode", help="H - Historic, D - Daily, W - Weekly, A - All")
    args   = parser.parse_args()
    if args.mode in ('H', 'D', 'W'):
        tech_leech(args.mode, args.stock)
    else:
        tech_leech('H', args.stock)
        tech_leech('W', args.stock)
        tech_leech('D', args.stock)
