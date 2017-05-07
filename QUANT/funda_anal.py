#!/usr/bin/env python
from __future__ import division
import requests
import argparse
import csv 
import math
import pandas as pd
import matplotlib.pyplot as     plt
from datetime import datetime, date
from dateutil import parser
from x4defs import *
import x4fns

def get_marketcap(stock):
    clog    = x4fns.read_csv(EQCatalog)
    mcap    = [x[PCAT['MCAP']] for x in clog if x[PCAT['NSECODE']] == stock][0]
    return int(mcap)

def get_currentprice(stock):
    tech_data   = x4fns.readall_csv(HISTDIR+stock+CSV)[-1]
    close       = float(tech_data[PHIST['CLOSE']])
    return close

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
    if stock == 'NIFTY':
        expanded = cum_funda(column, window)
    else:
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
            else:
                return []
    return expanded

def cum_funda(column, window):
    tech_data   = x4fns.readall_csv(HISTDIR+'NIFTY'+CSV)[-window:]
    dates       = [datetime.strptime(x[PHIST['DATE']], '%d %b %Y') for x in tech_data]
    close       = [float(x[PHIST['CLOSE']]) for x in tech_data]
    c_expanded  = [0] * window
    catalog     = x4fns.read_csv(EQCatalog)
    stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
    for stock in stocks:
        if column == 'SALES':
            if 'S' in stock['ratios']:
                expanded = expand_funda(stock['symbol'], 'SALES', window)
            elif 'I' in stock['ratios']:
                expanded = expand_funda(stock['symbol'], 'INCOME', window)
            else:
                expanded = []
        elif column == 'PAT':
            if 'O' in stock['ratios']:
                expanded = expand_funda(stock['symbol'], 'OPP', window)
            elif 'P' in stock['ratios']:
                expanded = expand_funda(stock['symbol'], 'PAT', window)
            else:
                expanded = []
        else:
            expanded = []
        if len(expanded) == window:
            c_expanded = [expanded[i][2]+c_expanded[i] for i in range(window)]
    nifty       = list(zip(dates, close, c_expanded))
    return nifty

def evaluate_bands(stock, column, window, mode='D'):
    expanded       = expand_funda(stock, column, window)
    if len(expanded):
        ps_value   = expanded[-1][2]
        ratio      = [x[1]/x[2] for x in expanded]
        rmean      = x4fns.smean(ratio)
        ratio      = [x/rmean for x in ratio]
        lratio     = ratio[-1]
        ltp        = expanded[-1][1]
        mean       = (1/lratio)*ltp
        stdd       = (x4fns.sstdd(ratio))*ltp
        upper      = (max(ratio)/lratio)*ltp
        lower      = (min(ratio)/lratio)*ltp
        start_date = expanded[0][0]
        data       = [[(expanded[i][0]-start_date).days, ratio[i]] for i in range(len(expanded))]
        slope, _   = x4fns.regress(data)
        slope      = int(slope*10000)
    else:
        mean       = None
        stdd       = None
        upper      = 0
        lower      = 0
        slope      = None
        ps_value   = 0
    if mode == 'S': # statistics
        return upper, lower, mean, stdd
    elif mode == 'P': # per share values
        return upper, lower, ps_value
    else:
        return upper, lower

if __name__ == '__main__':
    
    parser      = argparse.ArgumentParser("Fundamental Analysis")
    parser.add_argument("stock", help="name of stock")
    parser.add_argument("window", help="duration in trading days", type=int)
    args        = parser.parse_args()
    if args.stock == 'NIFTY' and args.window:
        plot_value  = 'SP'
    elif args.window:
        plot_value  = 'SIOP'
    else:
        plot_value  = 'SIOPF'
    quiet       = True
    mcap        = get_marketcap(args.stock)
    close       = get_currentprice(args.stock)
    if 'S' in plot_value and 'F' in plot_value:
        annualized    = annualize_funda(args.stock, 'SALES')
        df            = pd.DataFrame(annualized, columns=['YEAR', 'QTR', 'SALES'])
        df            = df.iloc[::-1]
        title         = 'S' if quiet else args.stock+' Sales'
        A = {'DF':df, 'title': title, 'X': 'YEAR', 'Y': ['SALES'], 'Z': []}
    elif 'S' in plot_value:
        expanded      = expand_funda(args.stock, 'SALES', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'SALES'])
        df['RATIO_S'] = (df['PRICE'] * mcap) / (df['SALES'] * close)
        df['MEAN_S']  = df['RATIO_S'].mean()
        df['MEAN_S']  = df['RATIO_S'].mean()
        df['UPPER_S'] = df['MEAN_S'] + df['RATIO_S'].std()
        df['LOWER_S'] = df['MEAN_S'] - df['RATIO_S'].std() 
        title         = 'S' if quiet else args.stock+' Sales'
        A = ({'DF':df, 'title': title, 'X': 'DATE',
              'Y': ['RATIO_S', 'MEAN_S', 'UPPER_S', 'LOWER_S'], 'Z': ['PRICE']})
    else:
        A = {}
    if 'I' in plot_value and 'F' in plot_value:
        annualized    = annualize_funda(args.stock, 'INCOME')
        df            = pd.DataFrame(annualized, columns=['YEAR', 'QTR', 'INCOME'])
        df            = df.iloc[::-1]
        title         = 'I' if quiet else args.stock+' Income'
        B = {'DF':df, 'title': title, 'X': 'YEAR', 'Y': ['INCOME'], 'Z': []}
    elif 'I' in plot_value:
        expanded      = expand_funda(args.stock, 'INCOME', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'INCOME'])
        df['RATIO_I'] = (df['PRICE'] * mcap) / (df['INCOME'] * close)
        df['MEAN_I']  = df['RATIO_I'].mean()
        df['MEAN_I']  = df['RATIO_I'].mean()
        df['UPPER_I'] = df['MEAN_I'] + df['RATIO_I'].std()
        df['LOWER_I'] = df['MEAN_I'] - df['RATIO_I'].std() 
        title         = 'I' if quiet else args.stock+' Income'
        B = ({'DF':df, 'title': title, 'X': 'DATE',
              'Y': ['RATIO_I', 'MEAN_I', 'UPPER_I', 'LOWER_I'], 'Z': ['PRICE']})
    else:
        B = {}
    if 'O' in plot_value and 'F' in plot_value:
        annualized    = annualize_funda(args.stock, 'OPP')
        df            = pd.DataFrame(annualized, columns=['YEAR', 'QTR', 'OPP'])
        df            = df.iloc[::-1]
        title         = 'O' if quiet else args.stock+' OpP'
        C = {'DF':df, 'title': title, 'X': 'YEAR', 'Y': ['OPP'], 'Z': []}
    elif 'O' in plot_value:
        expanded      = expand_funda(args.stock, 'OPP', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'OPP'])
        df['RATIO_O'] = (df['PRICE'] * mcap) / (df['OPP'] * close)
        df['MEAN_O']  = df['RATIO_O'].mean()
        df['MEAN_O']  = df['RATIO_O'].mean()
        df['UPPER_O'] = df['MEAN_O'] + df['RATIO_O'].std()
        df['LOWER_O'] = df['MEAN_O'] - df['RATIO_O'].std() 
        title         = 'O' if quiet else args.stock+' OpP'
        C = ({'DF':df, 'title': title, 'X': 'DATE',
              'Y': ['RATIO_O', 'MEAN_O', 'UPPER_O', 'LOWER_O'], 'Z': ['PRICE']})
    else:
        C = {}
    if 'P' in plot_value and 'F' in plot_value:
        annualized    = annualize_funda(args.stock, 'PAT')
        df            = pd.DataFrame(annualized, columns=['YEAR', 'QTR', 'PAT'])
        df            = df.iloc[::-1]
        title         = 'P' if quiet else args.stock+' Profit'
        D = {'DF':df, 'title': title, 'X': 'YEAR', 'Y': ['PAT'], 'Z': []}
    elif 'P' in plot_value:
        expanded      = expand_funda(args.stock, 'PAT', args.window)
        df            = pd.DataFrame(expanded, columns=['DATE', 'PRICE', 'PAT'])
        df['RATIO_P'] = (df['PRICE'] * mcap) / (df['PAT'] * close)
        df['MEAN_P']  = df['RATIO_P'].mean()
        df['MEAN_P']  = df['RATIO_P'].mean()
        df['UPPER_P'] = df['MEAN_P'] + df['RATIO_P'].std()
        df['LOWER_P'] = df['MEAN_P'] - df['RATIO_P'].std() 
        title         = 'P' if quiet else args.stock+' Profit'
        D = ({'DF':df, 'title': title, 'X': 'DATE',
              'Y': ['RATIO_P', 'MEAN_P', 'UPPER_P', 'LOWER_P'], 'Z': ['PRICE']})
    else:
        D = {}
    x4fns.multiplot_df(A=A, B=B, C=C, D=D)
