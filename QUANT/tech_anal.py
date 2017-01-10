#!/usr/bin/env python
import requests
import argparse
import math
import csv 
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

def autorgress(stock, duration, rwindow, mwindow):
    slen      = duration + rwindow + mwindow
    hist_data = x4fns.read_csv(HISTDIR+stock+CSV)
    price     = [[parser.parse(x[PHIST['DATE']]).date(), float(x[PHIST['CLOSE']])] for x in hist_data]
    
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
    return coeff, upper, lower, sgError

if __name__ == '__main__':
    
    argpar      = argparse.ArgumentParser("Fundamental Analysis")
    argpar.add_argument("stock", help="name of stock")
    argpar.add_argument("duration", help="analysis window in trading days", type=int)
    argpar.add_argument("rwindow", help="regression window in trading days", type=int)
    argpar.add_argument("mwindow", help="mean window in trading days", type=int)
    args        = argpar.parse_args()
    
    print (autorgress(args.stock, args.duration, args.rwindow, args.mwindow))
