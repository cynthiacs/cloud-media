
class MediaControllerProxy:
    def __init__(self, mqtt):
        print("MediaControllerProxy init")
        self._mqtt = mqtt

    def _get_request_topic(self, msg):
        jrpc = eval(msg)
        params = jrpc['params']
        nid = params['id']
        gid = params['group_id']
        vid = params['vendor_id']
        tag = "%s_%s_%s"%(vid, gid, nid)
        topic = "%s/%s/%s"%('media_controller', tag, 'request')
        return topic

    def send_request(self, msg):
        topic = self._get_request_topic(msg) 
        self._mqtt.publish(topic, msg, qos=2)

