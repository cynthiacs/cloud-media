from app import mqtt

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('ttt')
    print("on_connect......")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print("on_message")
    print(repr(data))

