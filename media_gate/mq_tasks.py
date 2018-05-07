from task import Task

class MqForwordTask(Task):
    def __init__(self, adaptor, tag, params):
        Task.__init__(self)
        print('MqForwordTask')

    def run(self):
        print('this is running MqForwordTask')
        # find the session with tag
        # send the data through the session's websocket


