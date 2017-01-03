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


def get_values(cells, pattern, cols):
    marker = 0
    for i, cell in enumerate(cells):
        if re.search(pattern, cell.text):
            marker = i
            break
    values  = []
    if marker:
        for cell in cells[marker+1:marker+1+cols]:
            try:
                value = float((cell.text).replace(',',''))
            except:
                value = cell.text
            values.append(value)
    else:
        values  = ['--']*cols
    return (values)


def parse_quarterly(html):
    qtr_defs  = {'Mar': 1, 'Jun':2, 'Sep':3, 'Dec':4}
    period_re = re.compile("(Mar|Jun|Sep|Dec) '([0-1][0-9])")
    sales_re  = re.compile('[Nn]et [Ss]ales/[Ii]ncome [Ff]rom [Oo]perations')
    incom_re  = re.compile('[Tt]otal [Ii]ncome [Ff]rom [Oo]perations')
    opp_re    = re.compile('P/L [Bb]efore [Oo]ther [Ii]nc.*[Ii]nt.*[Ee]xcpt.*[Tt]ax')
    pat_re    = re.compile('[Nn]et [Pp]rofit.*[Ff]or the [Pp]eriod')

    bs = BeautifulSoup(html, 'html.parser')
    tables = bs.findAll("table")
    table = tables[3]
    cells = table.findAll('td')

    periods, sales, pat, opp = ([] for i in range(4))
    for cell in cells:
        period = re.search(period_re, cell.text)
        if period:
            periods.append((qtr_defs[str(period.group(1))],  int(period.group(2))+2000)) 
    if len(periods):
        sales = get_values(cells, sales_re, len(periods))
        incom = get_values(cells, incom_re, len(periods))
        opp   = get_values(cells, opp_re, len(periods))
        pat   = get_values(cells, pat_re, len(periods))
    reports = []
    for i, period in enumerate(periods):
        reports.append([period[1],period[0],sales[i],incom[i],opp[i],pat[i]])
    return reports


def funda_leech(symbol, m='C', r='F'):
    """
    :param stocks: list of stocks
    :param mode: 'A' - All the historic data
                 'C' - Last five quarters
    :param r: 'C' - Consolidated
              'S' - Standalone
              'A' - Try both
              'F' - Find in Catalog
    :param date: Date used in the modes             
    """
    now       = datetime.now()
    catalog   = x4fns.read_csv(EQCatalog)
    rev_qtr   = ['Mar', 'Jun', 'Sep', 'Dec']

    catrow    = [x for x in catalog if x[PCAT['NSECODE']]==symbol][0]
    mccode    = catrow[PCAT['FCODE']]
    rep       = catrow[PCAT['CONS']] if r=='F' else r
    mode      = 'A' if m=='A' else 'C'
    try_qty   = True if rep == 'A' else False
    report    = 'quarterly' if rep == 'S' else 'cons_quarterly'
    nav       = 'curr'
    start     = str(now.year)+now.strftime('%m')
    end       = str(now.year)+now.strftime('%m')
    maxy      = str(now.year)+now.strftime('%m')
    print (symbol, mccode)
    cum_funda = []

    while True:
        params = {'nav':nav,'type':report,'sc_did':mccode,'start_year':start,'end_year':end,'max_year':maxy}
        
        # fetch the data
        if True:
            response = requests.post(FUNDAURL, data=params)
            html     = response.content
            fundas   = parse_quarterly(html)
            if (not len(fundas)) and (try_qty):
                report       = 'quarterly'
                try_qty      = False
            elif len(fundas):
                cum_funda.extend(fundas)
                if (mode == 'C'):
                    break
                else:
                    lastyear = fundas[-1][0]
                    lastqtr  = fundas[-1][1]
                    nav      = 'next'
                    end      = str(lastyear)+'{0:0=2d}'.format(lastqtr*3)
                try_qty      = False
            else:
                break
        else:
            break

    funda_file = FUNDADIR+symbol+CSV
    tocsv      = [['YEAR','QTR','SALES','INCOME','OPP','PAT']]
    if mode == 'A':
        tocsv.extend(cum_funda)
        x4fns.write_csv(funda_file, tocsv, 'w')
    else:
        existing   = x4fns.read_csv(funda_file)
        l_year     = existing[0][0]
        l_qtr      = int(existing[0][1])
        l_mth      = rev_qtr[l_qtr-1]
        l_date     = datetime.strptime(l_mth+' 30 '+l_year, '%b %d %Y')
        if ((now - l_date).days) > 105:
            cum_funda    = [x for x in cum_funda if (x[0]>int(l_year)) or ((x[0] == int(l_year)) and (x[1] > l_qtr))]
            tocsv.extend(cum_funda)
            tocsv.extend(existing)
            x4fns.write_csv(funda_file, tocsv, 'w')
    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Leech Stock Prices from MC")
    parser.add_argument("stock", help="name of stock")
    parser.add_argument("mode", help="A - All historic data, 'C' - Only update latest")
    parser.add_argument("report", help="C - Consolidated, S - Standalone, F - Find, A - Both")
    args   = parser.parse_args()

    funda_leech(args.stock, args.mode, args.report)
