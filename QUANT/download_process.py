from functools import partial
from multiprocessing.pool import Pool
from x4defs import *
import x4fns
from tech_leech import *

# Get the list of stocks
catalog     = x4fns.read_csv(EQCatalog)
stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
download    = partial(tech_leech, mode="H")
symbols     = [stock['symbol'] for stock in stocks]+['NIFTY']
with Pool(8) as p:
    p.map(download, symbols)
