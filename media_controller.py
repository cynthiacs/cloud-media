from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger

_REQUEST_ONLINE = 'online'


def handle_online(params):
    print(params)
    return "OK"


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='controller')
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_online)
    p2pc.loop()


