#!/usr/bin/env python
import requests
import sys
import csv 
import math
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

def autorgress(stocks, rwindow, mwindow):
    slen        = rwindow + mwindow
    out_file    = AREGRFILE
    aregress    = []
    for symbol in stocks:
        
        hist_file = HISTDIR+symbol+'.csv'
        with open(hist_file, 'r') as f:
            l = csv.reader(f)
            price = [[parser.parse(x[PHIST['DATE']]).date(), float(x[PHIST['CLOSE']])] for x in l]
        
        price     = price[-slen:]
        start_ts  = price[0][0]
        tseries   = [[(x[0]-start_ts).days, math.log(x[1])] for x in price]
        close     = [x[1] for x in price]
        close_log = [x[1] for x in tseries]
        regrP     = x4fns.rolling_regress(tseries, rwindow)
        rlen      = len(regrP)
        errorP    = [round((a/b-1)*100, 2) for a, b in zip(close_log[-rlen:], regrP)]
        muError   = x4fns.rolling_smean(errorP, mwindow)[0]
        sgError   = x4fns.rolling_sstdd(errorP, mwindow)[0]
        coeff     = int(muError*100/sgError)
        upper     = round((1+(muError + 1.5*sgError)/100)*close[-1], 2)
        lower     = round((1+(muError - 1.5*sgError)/100)*close[-1], 2)
        aregress.append([symbol, coeff, upper, lower, sgError])

    with open(out_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(aregress)

if __name__ == '__main__':
    
#    # Read the source file which contains all the details on the stocks
    catalog = x4fns.read_csv(EQCatalog)
    stocks  = [x[PCAT['NSECODE']] for x in catalog]
    
    autorgress(stocks, 252, 94)
