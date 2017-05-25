from x4defs import *
import x4fns
from tech_leech import *
from queue import Queue
from threading import Thread

class DownloadWorker(Thread):
   def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

   def run(self):
       while True:
           # Get the work from the queue and expand the tuple
           symbol = self.queue.get()
           tech_leech(symbol, 'H')
           self.queue.task_done()

queue = Queue()
# Create 8 worker threads
for x in range(8):
    worker = DownloadWorker(queue)
    # Setting daemon to True will let the main thread exit even though the workers are blocking
    worker.daemon = True
    worker.start()
# Get the list of stocks
catalog     = x4fns.read_csv(EQCatalog)
stocks      = [{'symbol':x[PCAT['NSECODE']], 'ratios':x[PCAT['RATIOS']]} for x in catalog]
# Put the tasks into the queue as a tuple
for symbol in [stock['symbol'] for stock in stocks]+['NIFTY']:
    print ("Leeching technical for stock: "+symbol)
    queue.put(symbol)
queue.join()
