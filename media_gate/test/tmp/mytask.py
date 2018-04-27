
from collections import deque

#class Task(object):
#    def __init__(self, co_task):
#        logger.debug("Task init")
#        self.task = co_task
#        self.sendval = None
#        self.stack = []
#
#    def awake_signal(self):
#        return "default_signal"
#
#    def run(self):
#        result = self.task.send(self.sendval)
#
#class schedule(object):
#    def __init__(self):
#        self.pending_tasks = deque()
#        self.running_tasks = deque()
#        self.num_running_task = 0
#
#    def schedule(self, task):
#        self.running_tasks.append(task)
#
#    def mainloop(self):
#        while self.num_running_task:
#            task = self.running_tasks.popleft()
#            try:
#                result = task.run()
#            except StopIteration:
#                self.num_running_task = -1
#            else:
#                pass


