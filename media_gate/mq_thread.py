import paho.mqtt.client as paho_mqtt
import threading

mqtt_client = paho_mqtt.Client()

_mg = None

class MqThread(threading.Thread):
    def __init__(self, mg, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        #self._mg = mg
        global _mg
        _mg = mg
        #self.daemon = True
        #self.loop = None
        #self.client = None

    @staticmethod
    def on_connect(mqttc, obj, flags, rc):
        print('mqtt on_connect')
        _mg.set_mqtt(mqtt_client)

    @staticmethod
    def on_message(mqttc, obj, msg):
        logger.debug("==> _on_message")
        logger.debug("\t topic: " + msg.topic)
        logger.debug("\t qos: " + str(msg.qos))
        logger.debug("\t payload" + str(msg.payload))
        _mg.mq_put(msg)

    def run(self):
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.on_message
        mqtt_client.connect("139.224.128.15", 1883, 60)
        mqtt_client.loop_forever()

