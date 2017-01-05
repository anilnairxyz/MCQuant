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
from x4gsheet import *

# Parameters 

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Batch Job to run all")
    parser.add_argument("-u", "--catalog", help="Update Catalog")
    parser.add_argument("-l", "--leech", help="Leech H: Historic, F:Fundamental")
    parser.add_argument("-f", "--funda", help="Analyse Fundamentals - S:Sales, I:Income, O:Op profit, P:PAT")
    args   = parser.parse_args()

    # Update the catalog
    if args.catalog:
        refresh_catalog()

    # Get the list of stocks
    catalog = x4fns.read_csv(EQCatalog)
    stocks  = [x[PCAT['NSECODE']] for x in catalog]
        
    # Fundamental Analysis
    if args.funda:
        header  = ['STOCK']
        if 'S' in args.funda:
            header.extend(['6M_S_Boll', '1Y_S_Boll', '2Y_S_Boll', '4Y_S_Boll',
                           '6M_S_Rang', '1Y_S_Rang', '2Y_S_Rang', '4Y_S_Rang',
                           '6M_S_Slop', '1Y_S_Slop', '2Y_S_Slop', '4Y_S_Slop'
                          ])
        if 'I' in args.funda:
            header.extend(['6M_I_Boll', '1Y_I_Boll', '2Y_I_Boll', '4Y_I_Boll',
                           '6M_I_Rang', '1Y_I_Rang', '2Y_I_Rang', '4Y_I_Rang',
                           '6M_I_Slop', '1Y_I_Slop', '2Y_I_Slop', '4Y_I_Slop'
                          ])
        if 'O' in args.funda:
            header.extend(['6M_O_Boll', '1Y_O_Boll', '2Y_O_Boll', '4Y_O_Boll',
                           '6M_O_Rang', '1Y_O_Rang', '2Y_O_Rang', '4Y_O_Rang',
                           '6M_O_Slop', '1Y_O_Slop', '2Y_O_Slop', '4Y_O_Slop'
                          ])
        if 'P' in args.funda:
            header.extend(['6M_P_Boll', '1Y_P_Boll', '2Y_P_Boll', '4Y_P_Boll',
                           '6M_P_Rang', '1Y_P_Rang', '2Y_P_Rang', '4Y_P_Rang',
                           '6M_P_Slop', '1Y_P_Slop', '2Y_P_Slop', '4Y_P_Slop'
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
