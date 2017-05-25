from x4defs import *
import x4fns
from tech_leech import *

# Get the list of stocks
catalog     = x4fns.read_csv(EQCatalog)
stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
for symbol in [stock['symbol'] for stock in stocks]+['NIFTY']:
    print ("Leeching technical for stock: "+symbol)
    tech_leech(symbol, 'H')
