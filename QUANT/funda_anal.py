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
    title       = ['-']*4
    if 'S' in args.value:
        df['RATIO_S'] = df['PRICE'] / df['SALES']
        df['MEAN_S']  = df['RATIO_S'].mean()
        df['UPPER_S'] = df['MEAN_S'] + df['RATIO_S'].std()
        df['LOWER_S'] = df['MEAN_S'] - df['RATIO_S'].std() 
        A = {'X': 'DATE', 'Y': ['RATIO_S', 'MEAN_S', 'UPPER_S', 'LOWER_S'], 'Z': ['PRICE']}
        title[0]      = args.stock+' Sales'
    else:
        A = {}
    if 'I' in args.value:
        df['RATIO_I'] = df['PRICE'] / df['INCOME']
        df['MEAN_I']  = df['RATIO_I'].mean()
        df['UPPER_I'] = df['MEAN_I'] + df['RATIO_I'].std()
        df['LOWER_I'] = df['MEAN_I'] - df['RATIO_I'].std() 
        B = {'X': 'DATE', 'Y': ['RATIO_I', 'MEAN_I', 'UPPER_I', 'LOWER_I'], 'Z': ['PRICE']}
        title[1]      = args.stock+' Income'
    else:
        B = {}
    if 'O' in args.value:
        df['RATIO_O'] = df['PRICE'] / df['OPP']
        df['MEAN_O']  = df['RATIO_O'].mean()
        df['UPPER_O'] = df['MEAN_O'] + df['RATIO_O'].std()
        df['LOWER_O'] = df['MEAN_O'] - df['RATIO_O'].std() 
        C = {'X': 'DATE', 'Y': ['RATIO_O', 'MEAN_O', 'UPPER_O', 'LOWER_O'], 'Z': ['PRICE']}
        title[2]      = args.stock+' OpP'
    else:
        C = {}
    if 'P' in args.value:
        df['RATIO_P'] = df['PRICE'] / df['PAT']
        df['MEAN_P']  = df['RATIO_P'].mean()
        df['UPPER_P'] = df['MEAN_P'] + df['RATIO_P'].std()
        df['LOWER_P'] = df['MEAN_P'] - df['RATIO_P'].std() 
        D = {'X': 'DATE', 'Y': ['RATIO_P', 'MEAN_P', 'UPPER_P', 'LOWER_P'], 'Z': ['PRICE']}
        title[3]      = args.stock+' PAT'
    else:
        D = {}
    x4fns.multiplot_df(df, title, A=A, B=B, C=C, D=D)
