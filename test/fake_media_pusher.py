
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger


REQUEST_START_PUSH_MEDIA = "startPushMedia"
REQUEST_STOP_PUSH_MEDIA = "stopPushMedia"


def on_start_push_media(params):
    print("params:" + repr(params))
    return "OK"


def on_stop_push_media(params):
    print("params:" + repr(params))
    return "OK"


def _listener(result):
    print("hello_listener")
    print("result: " + result)


if __name__ == '__main__':
    # id = IDManager.getID()
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='pusher1')
    p2pc.register_request_method(REQUEST_START_PUSH_MEDIA, on_start_push_media)
    p2pc.register_request_method(REQUEST_START_PUSH_MEDIA, on_stop_push_media)

    #whoami = 'pusher1'
    #str_time = '2017/11/16'
    #params = "{\"whoami\":\"" + whoami + "\"," + \
    #    "\"time\":\"" + str_time + "\"," + \
    #    "\"location\":\"longi lati\"}"
    params = r'{"whoami":"pusher1","time":"2017-12-07 16:08:32",' \
             r'"location":"none","nick":"pusher1","role":"pusher","status":"online"}'
    p2pc.send_rpc_request("controller", method="online", params=params, listener=_listener)
    p2pc.loop()
