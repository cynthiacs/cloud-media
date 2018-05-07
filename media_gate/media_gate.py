import logging.config
from queue import Queue
from ws_tasks import WsLoginTask, WsErrorTask
from mq_tasks import MqForwordTask 
from mg_adaptor import MgAdaptor

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

class MediaGate(object):
    def __init__(self):
        logger.debug("MediaGate init")
        self._input_queue = Queue()
        self.adaptor = MgAdaptor()

    def set_mqtt(self, mqtt):
        self.adaptor.set_mqtt(mqtt)

    def ws_put(self, ws, msg):
        # try:
        jrpc = eval(msg)
        method = jrpc['method']
        params = jrpc['params']
        if method == 'login': 
            task = WsLoginTask(self.adaptor, ws, params) 
        elif method == 'connect':
            #WsConnectTask(self.adaptor, params)
            pass
        elif method == 'start_push':
            pass
        elif method == 'stop_push':
            pass
        else:
            print("unsupported command %s" % (method,))
            task = WsErrorTask(self.adaptor, ws, '{"method":"echo", "params":"unsupported command"}') 

        self._input_queue.put(task) 

    def mq_put(self, params):
        print('fix me')
        tag = 'V0001_G0001_N0001'
        #params = 
        task = MqForwordTask(self.adaptor, tag, params)
        self._input_queue.put(task) 

    def get_task(self):
        task = self._input_queue.get()
        self._input_queue.task_done()
        return task
 
    def close(self):
        self._input_queue.put(None)
        self._input_queue.join()
       
