import time
import threading 
from media_gate import MediaGate


class MgThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self._mg= MediaGate()

    def ws_put(self, ws, msg):
        self._mg.ws_put(ws, msg) 

    def mq_put(self, msg):
        self._mg.mq_put(msg) 
 
    def set_mqtt(self, mqtt):
        self._mg.set_mqtt(mqtt)
   
    def stop(self):
        self._mg.close()
    
    def run(self):
        while True:
            task = self._mg.get_task()
            if task is None:
                break
            task.run()
        print("MgThread exit......")
        return

if __name__ == '__main__':
    w = MgThread()
    w.start()
    w.ws_put('123', '{"jsonrpc":2.0, "method":"login", "params":{"account":"yxd", "password":"123"}}')
    time.sleep(1)
    w.stop()

