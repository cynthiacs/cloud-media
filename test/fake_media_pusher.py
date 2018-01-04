
from p2p_mqtt.p2p_mqtt import P2PMqtt


REQUEST_START_PUSH_MEDIA = "startPushMedia"
REQUEST_STOP_PUSH_MEDIA = "stopPushMedia"


def on_start_push_media(params):
    print("params:" + repr(params))
    return "OK"


def on_stop_push_media(params):
    print("params:" + repr(params))
    return "OK"


def _listener(result):
    print("rpc listener")
    print("result: " + result)


if __name__ == '__main__':
    # id = IDManager.getID()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='pusher1')
    #p2pc.register_request_method(REQUEST_START_PUSH_MEDIA, on_start_push_media)
    #p2pc.register_request_method(REQUEST_START_PUSH_MEDIA, on_stop_push_media)

    #params = r'{"whoami":"pusher1","time":"2017-12-07 16:08:32",' \
    #         r'"location":"none","nick":"pusher1","role":"pusher","status":"online"}'

    #params = '{"id": "CloudMedia_9658983548343", "nick": "123", "role": "pusher",' \
    #         '"location": "unknown", "stream_status": "pushing_close", "vendor_id": "00000000",' \
    #         '"vendor_nick": "CM Team", "group_id": "00000000", "group_nick": "Default Group"}'

    params = '{"id": "CloudMedia_9658983548343", "nick": "123", "role": "puller",' \
             '"location": "unknown", "stream_status": "pushing_close", "vendor_id": "00000000",' \
             '"vendor_nick": "CM Team", "group_id": "00000000", "group_nick": "Default Group"}'
    p2pc.send_rpc_request("media_controller", method="Online", params=params, listener=_listener)
    #p2pc.send_rpc_request("controller", method="Offline", params=None, listener=_listener)

    p2pc.loop()
