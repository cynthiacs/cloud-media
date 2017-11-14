
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger


def _test_hello_handler(params):
    print("hello_handler")
    print("params:" + params)
    return "OK"


def _test_hello_listener(result):
    print("hello_listener")
    print("result: " + result)


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='alex')
    #p2pc.register_request_handler("hello", _test_hello_handler)
    p2pc.send_request("controller", "hello", "hhhhhh", _test_hello_listener)
    p2pc.loop()


