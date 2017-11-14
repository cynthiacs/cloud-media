
# python3 -m pip install paho-mqtt
# pip install paho-mqtt
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flag, rc):
    print("connect with result: " + str(rc))
    #client.subscribe("#")


def on_message(client, userdata, msg):
    print("==> on_message")
    print("\t topic:" + msg.topic)
    print("\t msg.payload:", msg.payload)


def on_request(mosq, obj, msg):
    print("on_request")
    print("\t MESSAGES: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_reply(mosq, obj, msg):
    print("on_reply")
    print("\t MESSAGES: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


class Test(object):
    def __init__(self):
        self.var = 10

    @staticmethod
    def on_connect(client, userdata, flag, rc):
        print("static on_connect")
        #print(client.var)

if __name__ == '__main__':
    client = mqtt.Client()
    client.message_callback_add("/controller/+/request", on_request)
    client.message_callback_add("/controller/+/reply", on_reply)

    #client.on_connect = on_connect
    tt = Test()
    client.on_connect = Test.on_connect
    client.on_message = on_message

    try:
        client.connect("139.224.128.15", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
