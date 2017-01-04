## ############################################################################################# ##
## Sub Routines
## ############################################################################################# ##
import math
import csv
import matplotlib.pyplot as     plt

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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

## Plots
## ================================================ ##
def plot_df(df, title, x, y, z=[]):
    cols        = y
    cols.append(x)
    cols.extend(z)
    df          = df[cols]
    df          = df.set_index([x])
    df.plot(title=title,figsize=(15,7), secondary_y=z, linewidth=2)
    plt.grid(True)
    plt.show()

## Multiple Plots
## ================================================ ##
def multiplot_df(A={}, B={}, C={}, D={}):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20,12))
    if A:
        cols        = A['Y']
        cols.append(A['X'])
        cols.extend(A['Z'])
        adf         = A['DF'][cols]
        adf         = adf.set_index([A['X']])
        adf.plot(title=A['title'], secondary_y=A['Z'], linewidth=2, legend=None, ax=axes[0,0])
    if B:
        cols        = B['Y']
        cols.append(B['X'])
        cols.extend(B['Z'])
        bdf         = B['DF'][cols]
        bdf         = bdf.set_index([B['X']])
        bdf.plot(title=B['title'], secondary_y=B['Z'], linewidth=2, legend=None, ax=axes[0,1])
    if C:
        cols        = C['Y']
        cols.append(C['X'])
        cols.extend(C['Z'])
        cdf         = C['DF'][cols]
        cdf         = cdf.set_index([C['X']])
        cdf.plot(title=C['title'], secondary_y=C['Z'], linewidth=2, legend=None, ax=axes[1,0])
    if D:
        cols        = D['Y']
        cols.append(D['X'])
        cols.extend(D['Z'])
        ddf         = D['DF'][cols]
        ddf         = ddf.set_index([D['X']])
        ddf.plot(title=D['title'], secondary_y=D['Z'], linewidth=2, legend=None, ax=axes[1,1])
    plt.grid(True)
    plt.show()
