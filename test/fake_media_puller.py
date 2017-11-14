import time
import threading

from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger


REQUEST_START_PUSH_MEDIA = "startPushMedia"
REQUEST_STOP_PUSH_MEDIA = "stopPushMedia"


def _listener(result):
    print("hello_listener")
    print("result: " + result)


def worker(p2pc, interval):
    while True:
        time.sleep(interval)
        p2pc.send_request("pusher1", REQUEST_START_PUSH_MEDIA, "hhhhhh", _listener)
        time.sleep(interval)
        p2pc.send_request("pusher1", REQUEST_STOP_PUSH_MEDIA, "hhhhhh", _listener)


if __name__ == '__main__':
    # id = IDManager.getID()
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='puller1')
    t = threading.Thread(target=worker, args=(p2pc, 3))
    t.start()
    p2pc.loop()


