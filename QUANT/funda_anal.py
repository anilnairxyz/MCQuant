#!/usr/bin/env python
from __future__ import division
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

def annualize_funda(stock, column):
    raw     = x4fns.read_csv(FUNDADIR+stock+CSV)
    funda   = []
    for row in raw:
        if x4fns.is_number(row[PFUNDA[column]]):
            funda.append([row[PFUNDA['YEAR']], row[PFUNDA['QTR']], row[PFUNDA[column]]])
        else:        
            break
    annualized = []
    for i, row in enumerate(funda[:-3]):
        ann_row = row[:2]
        ann_row.append(sum([float(funda[x][2]) for x in range(i, i+4)]))
        annualized.append(ann_row)
    return annualized

def expand_funda(stock, column, window):
    qtr_dates   = ['31 Mar', '30 Jun', '30 Sep', '31 Dec']
    annualized  = annualize_funda(stock, column)
    tech_data   = x4fns.readall_csv(HISTDIR+stock+CSV)[-window:]
    dates       = [datetime.strptime(x[PHIST['DATE']], '%d %b %Y') for x in tech_data]
    close       = [float(x[PHIST['CLOSE']]) for x in tech_data]
    expanded    = []
    for j, date in enumerate(dates):
        for row in annualized:
            if date > datetime.strptime(qtr_dates[int(row[1])-1]+row[0], '%d %b%Y'):
                expanded.append([date, close[j], row[-1]])
                break
    return expanded

def evaluate_bands(stock, column, window):
    expanded       = expand_funda(stock, column, window)
    if len(expanded):
        ratio      = [x[1]/x[2] for x in expanded]
        mean       = x4fns.smean(ratio)
        stdd       = x4fns.sstdd(ratio)
        bollinger  = int((ratio[-1] - mean)*100/stdd)
        upper      = max(ratio)
        lower      = min(ratio)
        rangeband  = int((ratio[-1] - lower)*100/(upper - lower))
        start_date = expanded[0][0]
        data       = [[(x[0]-start_date).days, x[1]/x[2]] for x in expanded]
        slope, _   = x4fns.regress(data)
        slope      = int(slope*10000)
    else:
        bollinger  = 'Null'
        rangeband  = 'Null'
        slope      = 'Null'
    return bollinger, rangeband, slope

if __name__ == '__main__':
    
    parser      = argparse.ArgumentParser("Fundamental Analysis")
    parser.add_argument("stock", help="name of stock")
    parser.add_argument("window", help="duration in trading days", type=int)
    parser.add_argument("value", help="Value for testing - 'S':Sales, 'I':Income, 'O':Op profit, 'P':PAT")
    args        = parser.parse_args()
    if 'S' in args.value:
        expanded      = expand_funda(args.stock, 'SALES', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'SALES'])
        df['RATIO_S'] = df['PRICE'] / df['SALES']
        df['MEAN_S']  = df['RATIO_S'].mean()
        df['RATIO_S'] = df['RATIO_S'] / df['MEAN_S']
        df['MEAN_S']  = df['RATIO_S'].mean()
        df['UPPER_S'] = df['MEAN_S'] + df['RATIO_S'].std()
        df['LOWER_S'] = df['MEAN_S'] - df['RATIO_S'].std() 
        title         = args.stock+' Sales'
        A = {'DF':df, 'title':title, 'X': 'DATE', 'Y': ['RATIO_S', 'MEAN_S', 'UPPER_S', 'LOWER_S'], 'Z': ['PRICE']}
    else:
        A = {}
    if 'I' in args.value:
        expanded      = expand_funda(args.stock, 'INCOME', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'INCOME'])
        df['RATIO_I'] = df['PRICE'] / df['INCOME']
        df['MEAN_I']  = df['RATIO_I'].mean()
        df['RATIO_I'] = df['RATIO_I'] / df['MEAN_I']
        df['MEAN_I']  = df['RATIO_I'].mean()
        df['UPPER_I'] = df['MEAN_I'] + df['RATIO_I'].std()
        df['LOWER_I'] = df['MEAN_I'] - df['RATIO_I'].std() 
        title         = args.stock+' Income'
        B = {'DF':df, 'title':title, 'X': 'DATE', 'Y': ['RATIO_I', 'MEAN_I', 'UPPER_I', 'LOWER_I'], 'Z': ['PRICE']}
    else:
        B = {}
    if 'O' in args.value:
        expanded      = expand_funda(args.stock, 'OPP', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'OPP'])
        df['RATIO_O'] = df['PRICE'] / df['OPP']
        df['MEAN_O']  = df['RATIO_O'].mean()
        df['RATIO_O'] = df['RATIO_O'] / df['MEAN_O']
        df['MEAN_O']  = df['RATIO_O'].mean()
        df['UPPER_O'] = df['MEAN_O'] + df['RATIO_O'].std()
        df['LOWER_O'] = df['MEAN_O'] - df['RATIO_O'].std() 
        title         = args.stock+' OpP'
        C = {'DF':df, 'title':title, 'X': 'DATE', 'Y': ['RATIO_O', 'MEAN_O', 'UPPER_O', 'LOWER_O'], 'Z': ['PRICE']}
    else:
        C = {}
    if 'P' in args.value:
        expanded      = expand_funda(args.stock, 'PAT', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'PAT'])
        df['RATIO_P'] = df['PRICE'] / df['PAT']
        df['MEAN_P']  = df['RATIO_P'].mean()
        df['RATIO_P'] = df['RATIO_P'] / df['MEAN_P']
        df['MEAN_P']  = df['RATIO_P'].mean()
        df['UPPER_P'] = df['MEAN_P'] + df['RATIO_P'].std()
        df['LOWER_P'] = df['MEAN_P'] - df['RATIO_P'].std() 
        title         = args.stock+' PAT'
        D = {'DF':df, 'title':title, 'X': 'DATE', 'Y': ['RATIO_P', 'MEAN_P', 'UPPER_P', 'LOWER_P'], 'Z': ['PRICE']}
    else:
        D = {}
    x4fns.multiplot_df(A=A, B=B, C=C, D=D)
