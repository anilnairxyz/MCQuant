#!/usr/bin/env python
import requests
import argparse
import sys
import csv 
import math
import pandas as pd
import matplotlib.pyplot as     plt
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

qtr_dates = ['31 Mar', '30 Jun', '30 Sep', '31 Dec']
HFUNDA    = ['DATE','QTR','SALES','INCOME','OPP','PAT']

def annualize_funda(stock):
    funda = x4fns.read_csv(FUNDADIR+stock+CSV)
    annualized = []
    for i, row in enumerate(funda[:-3]):
        ann_row = row[:2]
        ann_row.append(sum([float(funda[x][2]) for x in range(i, i+4)]))
        ann_row.append(sum([float(funda[x][3]) for x in range(i, i+4)]))
        ann_row.append(sum([float(funda[x][4]) for x in range(i, i+4)]))
        ann_row.append(sum([float(funda[x][5]) for x in range(i, i+4)]))
        annualized.append(ann_row)
    return annualized

def expand_funda(funda, stock, dates):
    expanded = []
    for date in dates:
        exp_row = [date]
        for i, row in enumerate(funda):
            if date > datetime.strptime(qtr_dates[int(row[1])-1]+row[0], '%d %b%Y'):
                for cell in row[1:]:
                    exp_row.append(cell)
                break
        expanded.append(exp_row)
    return expanded

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser("Fundamental Analysis")
    parser.add_argument("stock", help="name of stock")
    parser.add_argument("window", help="duration in trading days", type=int)
    parser.add_argument("value", help="Value for testing - 'S':Sales, 'I':Income, 'O':Op profit, 'P':PAT")
    args   = parser.parse_args()
    tech_data   = x4fns.readall_csv(HISTDIR+args.stock+CSV)[-args.window:]
    dates       = [datetime.strptime(x[PHIST['DATE']], '%d %b %Y') for x in tech_data]
    close       = [float(x[PHIST['CLOSE']]) for x in tech_data]
    annualized  = annualize_funda(args.stock)
    expanded    = expand_funda(annualized, args.stock, dates)
    df          = pd.DataFrame(expanded, columns=HFUNDA)
    df['PRICE'] = close
    if args.value == 'S':
        df['RATIO'] = df['PRICE'] / df['SALES']
    elif args.value == 'I':
        df['RATIO'] = df['PRICE'] / df['INCOME']
    elif args.value == 'O':
        df['RATIO'] = df['PRICE'] / df['OPP']
    else:
        df['RATIO'] = df['PRICE'] / df['PAT']
    df['MEAN']  = df['RATIO'].mean()
    df['UPPER'] = df['MEAN'] + df['RATIO'].std()
    df['LOWER'] = df['MEAN'] - df['RATIO'].std() 
#    last_close  = close[-1]
#    last_ratio  = df['RATIO'].iloc[-1]
#    print (last_close, last_ratio)
    x4fns.plot_df(df, 'DATE', ['RATIO', 'MEAN', 'UPPER', 'LOWER'], ['PRICE'], args.stock)
#    x4fns.write_csv('aaa.csv', annualized, 'w')
