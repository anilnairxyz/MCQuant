#!/usr/bin/env python
import requests
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

def plot_df(df, x, y, z, title):
    cols        = y
    cols.append(x)
    cols.extend(z)
    df          = df[cols]
    df          = df.set_index([x])
    df.plot(title=title,figsize=(15,7), secondary_y=z, linewidth=2)
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    
#    # Read the source file which contains all the details on the stocks
#    catalog     = x4fns.read_csv(EQCatalog)
#    stocks      = [x[PCAT['NSECODE']] for x in catalog]
    stock       = str(sys.argv[1])
    sample_size = int(sys.argv[2])
    ratio       = str(sys.argv[3])
    tech_data   = x4fns.readall_csv(HISTDIR+stock+CSV)[-sample_size:]
    dates       = [datetime.strptime(x[PHIST['DATE']], '%d %b %Y') for x in tech_data]
    close       = [float(x[PHIST['CLOSE']]) for x in tech_data]
    annualized  = annualize_funda(stock)
    expanded    = expand_funda(annualized, stock, dates)
    df          = pd.DataFrame(expanded, columns=HFUNDA)
    df['PRICE'] = close
    if ratio == 'S':
        df['RATIO'] = df['PRICE'] / df['SALES']
    elif ratio == 'I':
        df['RATIO'] = df['PRICE'] / df['INCOME']
    elif ratio == 'O':
        df['RATIO'] = df['PRICE'] / df['OPP']
    else:
        df['RATIO'] = df['PRICE'] / df['PAT']
    df['MEAN']  = df['RATIO'].mean()
    df['UPPER'] = df['MEAN'] + df['RATIO'].std()
    df['LOWER'] = df['MEAN'] - df['RATIO'].std() 
    print (df)
    plot_df(df, 'DATE', ['RATIO', 'MEAN', 'UPPER', 'LOWER'], ['PRICE'], stock)
    x4fns.write_csv('aaa.csv', annualized, 'w')
