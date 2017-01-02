#!/usr/bin/env python
import requests
import sys
import csv 
import math
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

def tech_leech(mode, stocks):

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
    
    for symbol in stocks:
        
        if symbol != 'NIFTY':
            catrow = [x for x in catalog if x[PCAT['NSECODE']]==symbol][0]
            mc_code = catrow[PCAT['MCCODE']]
        else:
            mc_code = 'nifty'
        url = mc_url+mc_code+'.csv'
    
        # fetch the data
        response = requests.get(url)
        html = response.content
        
        #create the output file
        output_file = open(output_dir+symbol+'.csv', "w+")
    
        #write to the respective files
        html = html.decode('utf-8')
        output_file.write(html)
        output_file.close()

if __name__ == '__main__':
    
#    # Read the source file which contains all the details on the stocks
    catalog = x4fns.read_csv(EQCatalog)
    stocks  = [x[PCAT['NSECODE']] for x in catalog]
    stocks.append('NIFTY')
    tech_leech('H', stocks)
#    tech_leech('W', stocks)
#    tech_leech('D', stocks)
