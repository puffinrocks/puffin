from queue import Queue
from threading import Thread
from .. import app

# Based on http://code.activestate.com/recipes/577187-python-thread-pool/


queue = None

def init():
    global queue
    threads = 1
    queue = Queue()
    for _ in range(threads): 
        Worker(queue)

def task(func, *args, **kwargs):
    queue.put((func, args, kwargs))
    
def wait():
    queue.join()

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kwargs = self.queue.get()
            try: 
                func(*args, **kwargs)
            except Exception as e: 
                app.logger.warn("Error processing task", e)
            self.queue.task_done()

