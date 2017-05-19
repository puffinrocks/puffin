import queue as queue_module
import threading

from puffin import app
from .. import util


# Based on http://code.activestate.com/recipes/577187-python-thread-pool/

queue = None

task_ids = util.SafeSet()


def init():
    global queue
    threads = 1
    queue = queue_module.Queue()
    for _ in range(threads):
        Worker(queue)

def task(task_id, func, *args, **kwargs):
    if task_id:
        task_ids.add(task_id)
    queue.put((task_id, func, args, kwargs))

def task_exists(task_id):
    return task_ids.contains(task_id)

def wait():
    queue.join()

class Worker(threading.Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            task_id, func, args, kwargs = self.queue.get()
            try:
                with app.app_context():
                    func(*args, **kwargs)
            except Exception as e:
                app.logger.warn("Error processing task", exc_info=e)
            finally:
                self.queue.task_done()
                if task_id:
                    task_ids.remove(task_id)

