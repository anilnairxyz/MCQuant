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
from tech_leech import *
from funda_leech import *
from funda_anal import *

# Parameters 

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Batch Job to run all")
    parser.add_argument("-s", "--stock", help="name of stock")
    parser.add_argument("-l", "--leech", help="Leech H: Historic, F:Fundamental")
    parser.add_argument("-f", "--funda", help="Analyse Fundamentals - S:Sales, I:Income, O:Op profit, P:PAT")
#    parser.add_argument("window", help="duration in trading days", type=int)
    args   = parser.parse_args()
    if args.stock:
        stocks = [args.stock]
    else:
        # Read the source file which contains all the details on the stocks
        catalog = x4fns.read_csv(EQCatalog)
        stocks  = [x[PCAT['NSECODE']] for x in catalog]
        
    if args.funda:
        header  = ['STOCK']
        if 'S' in args.funda:
            header.extend(['6M_SAL_BollB', '1Y_SAL_BollB', '2Y_SAL_BollB', '4Y_SAL_BollB',
                          '6M_SAL_Range', '1Y_SAL_Range', '2Y_SAL_Range', '4Y_SAL_Range',
                          '6M_SAL_Slope', '1Y_SAL_Slope', '2Y_SAL_Slope', '4Y_SAL_Slope'
                          ])
        if 'I' in args.funda:
            header.extend(['6M_INC_BollB', '1Y_INC_BollB', '2Y_INC_BollB', '4Y_INC_BollB',
                          '6M_INC_Range', '1Y_INC_Range', '2Y_INC_Range', '4Y_INC_Range',
                          '6M_INC_Slope', '1Y_INC_Slope', '2Y_INC_Slope', '4Y_INC_Slope'
                          ])
        if 'O' in args.funda:
            header.extend(['6M_OPP_BollB', '1Y_OPP_BollB', '2Y_OPP_BollB', '4Y_OPP_BollB',
                          '6M_OPP_Range', '1Y_OPP_Range', '2Y_OPP_Range', '4Y_OPP_Range',
                          '6M_OPP_Slope', '1Y_OPP_Slope', '2Y_OPP_Slope', '4Y_OPP_Slope'
                          ])
        if 'P' in args.funda:
            header.extend(['6M_PAT_BollB', '1Y_PAT_BollB', '2Y_PAT_BollB', '4Y_PAT_BollB',
                          '6M_PAT_Range', '1Y_PAT_Range', '2Y_PAT_Range', '4Y_PAT_Range',
                          '6M_PAT_Slope', '1Y_PAT_Slope', '2Y_PAT_Slope', '4Y_PAT_Slope'
                          ])
        funda   = [header]

    for stock in stocks:

        print ("Processing for stock: "+stock)
        if args.leech:
            # Leech technical information (price / volume)
            if 'H' in args.leech:
                tech_leech(stock, 'H')
            if 'D' in args.leech:
                tech_leech(stock, 'D')
            if 'W' in args.leech:
                tech_leech(stock, 'W')
            # Leech fundamental information (sales, profit etc.)
            if 'F' in args.leech:
                funda_leech(stock, 'C', 'F')

        if args.funda:
            row = [stock]
            if 'S' in args.funda:
                s_bb_6m, s_rb_6m, s_sl_6m = evaluate_bands(stock, 'SALES', 126)
                s_bb_1y, s_rb_1y, s_sl_1y = evaluate_bands(stock, 'SALES', 252)
                s_bb_2y, s_rb_2y, s_sl_2y = evaluate_bands(stock, 'SALES', 504)
                s_bb_4y, s_rb_4y, s_sl_4y = evaluate_bands(stock, 'SALES', 1008)
                row.extend([s_bb_6m,s_bb_1y,s_bb_2y,s_bb_4y,s_rb_6m,s_rb_1y,s_rb_2y,s_rb_4y,s_sl_6m,s_sl_1y,s_sl_2y,s_sl_4y])
            if 'I' in args.funda:
                i_bb_6m, i_rb_6m, i_sl_6m = evaluate_bands(stock, 'INCOME', 126)
                i_bb_1y, i_rb_1y, i_sl_1y = evaluate_bands(stock, 'INCOME', 252)
                i_bb_2y, i_rb_2y, i_sl_2y = evaluate_bands(stock, 'INCOME', 504)
                i_bb_4y, i_rb_4y, i_sl_4y = evaluate_bands(stock, 'INCOME', 1008)
                row.extend([i_bb_6m,i_bb_1y,i_bb_2y,i_bb_4y,i_rb_6m,i_rb_1y,i_rb_2y,i_rb_4y,i_sl_6m,i_sl_1y,i_sl_2y,i_sl_4y])
            if 'O' in args.funda:
                o_bb_6m, o_rb_6m, o_sl_6m = evaluate_bands(stock, 'OPP', 126)
                o_bb_1y, o_rb_1y, o_sl_1y = evaluate_bands(stock, 'OPP', 252)
                o_bb_2y, o_rb_2y, o_sl_2y = evaluate_bands(stock, 'OPP', 504)
                o_bb_4y, o_rb_4y, o_sl_4y = evaluate_bands(stock, 'OPP', 1008)
                row.extend([o_bb_6m,o_bb_1y,o_bb_2y,o_bb_4y,o_rb_6m,o_rb_1y,o_rb_2y,o_rb_4y,o_sl_6m,o_sl_1y,o_sl_2y,o_sl_4y])
            if 'P' in args.funda:
                p_bb_6m, p_rb_6m, p_sl_6m = evaluate_bands(stock, 'PAT', 126)
                p_bb_1y, p_rb_1y, p_sl_1y = evaluate_bands(stock, 'PAT', 252)
                p_bb_2y, p_rb_2y, p_sl_2y = evaluate_bands(stock, 'PAT', 504)
                p_bb_4y, p_rb_4y, p_sl_4y = evaluate_bands(stock, 'PAT', 1008)
                row.extend([p_bb_6m,p_bb_1y,p_bb_2y,p_bb_4y,p_rb_6m,p_rb_1y,p_rb_2y,p_rb_4y,p_sl_6m,p_sl_1y,p_sl_2y,p_sl_4y])

        funda.append(row)

    if args.funda:
        x4fns.write_csv(DBDIR+'Fundamental_Analysis'+CSV, funda, 'w')
