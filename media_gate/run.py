from ws_thread import WsThread
from mqtt_thread import MqThread


if __name__ == '__main__':
    ws_thread = WsThread()
    ws_thread.start()

    mq_thread = MqThread()
    mq_thread.start()

    while(True):
        pass
