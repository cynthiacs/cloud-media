import paho.mqtt.client as paho_mqtt
import threading
import asyncio
from mg_adaptor import mg_adaptor
from mq_tasks import mq_forward_reply 

class MqttWrapper(paho_mqtt.Client):
    def __init__(self):
        # the default parameters:
        # client_id = "", clean_session = True, userdata = None,
        # protocol = MQTTv311, transport = "tcp"
        super().__init__()
        self._main_loop = None

    def set_loop(self, loop):
        self._main_loop = loop

    def send_corutine(self, co):
        asyncio.run_coroutine_threadsafe(co, self._main_loop) 

    def send_callable(self, ca, msg):
        self._main_loop.call_soon_threadsafe(ca, msg)

_mqtt_client = MqttWrapper()


class MqThread(threading.Thread):
    def __init__(self, main_loop, *args, **kwargs):
        global _main_loop
        threading.Thread.__init__(self, *args, **kwargs)
        _mqtt_client.set_loop(main_loop)
        #self.daemon = True
        #self.loop = None
        #self.client = None

    @staticmethod
    def on_connect(mqttc, obj, flags, rc):
        print('mqtt on_connect')
        
        mg_adaptor.set_mqtt(mqttc)

    @staticmethod
    def on_message(mqttc, obj, msg):
        print("==> _on_message")
        print("\t topic: " + msg.topic)
        print("\t qos: " + str(msg.qos))
        print("\t payload" + str(msg.payload))

        asyncio.run_coroutine_threadsafe(mq_forward_reply(msg), mqttc._main_loop)
        #mqttc.send_callable(mq_forward_reply, msg)

    def run(self):
        _mqtt_client.on_connect = self.on_connect
        _mqtt_client.on_message = self.on_message
        _mqtt_client.connect("139.224.128.15", 1883, 60)
        _mqtt_client.loop_forever()

