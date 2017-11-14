
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger


REQUEST_START_PUSH_MEDIA = "startPushMedia"
REQUEST_STOP_PUSH_MEDIA = "stopPushMedia"


def on_start_push_media(params):
    print("params:" + params)
    return "OK"


def on_stop_push_media(params):
    print("params:" + params)
    return "OK"


if __name__ == '__main__':
    # id = IDManager.getID()
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='pusher1')
    p2pc.register_request_handler(REQUEST_START_PUSH_MEDIA, on_start_push_media)
    p2pc.register_request_handler(REQUEST_START_PUSH_MEDIA, on_stop_push_media)
    p2pc.loop()
