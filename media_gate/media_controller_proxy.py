
class MediaControllerProxy:
    def __init__(self, mqtt):
        print("MediaControllerProxy init")
        self._mqtt = mqtt

    def _get_request_topic(self, tag):
        topic = "%s/%s/%s"%('media_controller', tag, 'request')
        return topic

    def sub(self, topic, qos=2):
        print("subscribe \n\t %s \n\t %s" %
            ("topic: " + topic, "qos: " + str(qos)))
 
        self._mqtt.subscribe(topic, qos)

    def unsub(self, topic):
        print("unsubscribe topic %s" % (topic,) )
 
        self._mqtt.unsubscribe(topic)

    def send_request(self, tag, msg):
        topic = self._get_request_topic(tag) 
        self._mqtt.publish(topic, msg, qos=2)

