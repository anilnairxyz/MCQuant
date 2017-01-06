## ********************************************************************************************* ##
## The header module contains CONSTANT definitions and type declarations for directory structure ##
## and DATABASE TABLE headers                                                                    ##
## ********************************************************************************************* ##

## ============================================================================================= ##
## GENERAL 
## ============================================================================================= ##
CSV                = '.csv'
JSON               = '.json'
BASEDIR            = '../'

# MC url paths
TECHURL            = 'http://www.moneycontrol.com/tech_charts/nse/'
HISTURL            = TECHURL+'his/'
WEEKURL            = TECHURL+'week/'
DAYURL             = TECHURL+'int/'

FUNDAURL           = "http://www.moneycontrol.com/stocks/company_info/print_financials.php"

## Directory Structure
DBDIR              = BASEDIR+'DATABASE/'
TABLEDIR           = BASEDIR+'TABLES/'
HISTDIR            = DBDIR+'HISTORIC/'
WEEKDIR            = DBDIR+'WEEKLY/'
DAYDIR             = DBDIR+'DAILY/'
FUNDADIR           = DBDIR+'FUNDAMENTALS/'
AREGRFILE          = DBDIR+'AREGRESS'+CSV

## Files for EQUITY DB
EQCatalog          = TABLEDIR+'EQCatalog'+CSV

## Column Names/Types for the EQUITY Databases 
PCAT            = {'RATING':0,'NSECODE':1,'MCCODE':2,'FCODE':3,'CONS':4,'ISIN':5,\
        'NAME':6,'LISTING_DATE':7,'SECTOR':8,'INDUSTRY':9,'RATIOS':10}
PHIST           = {'DATE':0,'OPEN':1,'HIGH':2,'LOW':3,'CLOSE':4,'VOLUME':5}
PWEEK           = {'DATE':0,'TIME':1,'CLOSE':2,'VOLUME':3}
PDAY            = {'TIME':0,'CLOSE':1,'VOLUME':2}
PFUNDA          = {'YEAR':0,'QTR':1,'SALES':2,'INCOME':3,'OPP':4,'PAT':5}
