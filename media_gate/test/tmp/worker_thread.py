import threading
from queue import Queue

class WorkerThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.input_queue = Queue()

    def send(self, item):
        self.input_queue.put(item)

    def close(self):
        self.input_queue.put(None)
        self.input_queue.join()

    def run(self):
        while True:
            item = self.input_queue.get()
            if item is None:
                break
            # do some thing
            print(item)
            self.input_queue.task_done()

        self.input_queue.task_done()
        return

if __name__ == '__main__':
    w = WorkerThread()
    w.start()
    w.send('hello')
    w.send('world')
    w.close()

