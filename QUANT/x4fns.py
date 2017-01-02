## ############################################################################################# ##
## Sub Routines
## ############################################################################################# ##
import math
import csv

## ********************************************************************************************* ##
## CSV Related
## ********************************************************************************************* ##
## Read a csv file and put all lines into list
## =========================================== ##
def readall_csv(fname):
    with open(fname, 'r') as f:
        reader         = csv.reader(f)
        flist          = list(reader)
        return flist

## Read a csv file and put non header lines into list
## =========================================== ##
def read_csv(fname):
    with open(fname, 'r') as f:
        reader         = csv.reader(f)
        next(reader)
        flist          = list(reader)
        return flist

## Read a csv file and put header line into list
## =========================================== ##
def readhdr_csv(fname):
    with open(fname, 'r') as f:
        reader         = csv.reader(f)
        flist          = []
        flist.append(list(next(reader)))
        return flist

## Append / Write a list to a csv file 
## =========================================== ##
def write_csv(fname, flist, mode):
    f        = open(fname, mode)
    fwriter  = csv.writer(f, lineterminator='\n')
    for row in flist:
        fwriter.writerow(row)
    f.close()

## ********************************************************************************************* ##
## Statistics
## ********************************************************************************************* ##
## Find mean of a list
## =========================================== ##
def smean(data):
    mean           = sum(data)/len(data)
    return mean

## Find standard deviation
## =========================================== ##
def sstdd(data):
    mean           = smean(data)
    error          = [(x-mean)**2 for x in data]
    variance       = sum(error) / (len(data)-1)
    stdd           = variance**0.5
    return stdd

## Find rolling sma of a list
## =========================================== ##
def rolling_smean(data, window):
    rsmean          = []
    for i in range(window, len(data)):
        rsmean.append(round(smean(data[i-window:i]), 2)) 
    return rsmean    

## Find rolling stdd of a list
## =========================================== ##
def rolling_sstdd(data, window):
    rsstdd          = []
    for i in range(window, len(data)):
        rsstdd.append(round(sstdd(data[i-window:i]), 2)) 
    return rsstdd    

## Find slope and intercept of linear regression
## =========================================== ##
def regress(data):
    x              = [d[0] for d in data]
    y              = [d[1] for d in data]
    xmu            = smean(x)
    ymu            = smean(y)
    num            = [(x[i]-xmu)*(y[i]-ymu) for i in range(0,len(x))]
    den            = [(x[i]-xmu)*(x[i]-xmu) for i in range(0,len(x))]
    slope          = sum(num)/sum(den)
    intercept      = ymu - slope*xmu
    return slope, intercept

## Find regression expected value of a list
## =========================================== ##
def regpred(data):
    slope, intercept   = regress(data)
    predict            = data[-1][0]*slope + intercept
    return predict

## Find rolling regression expected value of a list
## ================================================ ##
def rolling_regress(data, window):
    rpred          = []
    for i in range(0, len(data)-window+1):
        rpred.append(regpred(data[i:i+window])) 
    return rpred    
