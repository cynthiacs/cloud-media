from mg_thread import MgThread
from ws_thread import WsThread
from mq_thread import MqThread

mg_thread = None

if __name__ == '__main__':
    mg_thread = MgThread()
    mg_thread.start()

    ws_thread = WsThread(mg_thread)
    ws_thread.start()

    mq_thread = MqThread(mg_thread)
    mq_thread.start()

    while(True):
        pass
