from flask import Flask
from flask import request
import paho.mqtt.client as mqtt


app = Flask(__name__)


_ID = 0
@app.route('/get_id')
def get_id():
    global _ID
    _ID += 1
    return str(_ID)


def _mqtt_publish(topic, payload):
    mqttc = mqtt.Client()
    mqttc.connect("139.224.128.15", 1883, 60)

    mqttc.loop_start()
    infot = mqttc.publish(topic, payload, qos=2)
    infot.wait_for_publish()

@app.route('/cm_live_steams_notify')
def cm_live_steams_notify():
    # print(request.data)
    """
    request.args: the key / value pairs in the URL query string
    request.form: the key / value pairs in the body, 
        from a HTML post form, or JavaScript request that isn't JSON encoded
    request.files: the files in the body, which Flask keeps separate from form.
        HTML forms must use enctype = multipart / form - data or files will not be uploaded.
    request.values: combined args and form, preferring args if keys overlap
    for url query params:
        search = request.args.get("search")
        page = request.args.get("page")
    for form input:
        email = request.form.get('email')
        password = request.form.get('password')
    for data type application/json:
        data = request.data
        dataDict = json.loads(data)

    print("action: ", request.args.get("action"))
    print("ip: ", request.args.get("ip"))
    print("id: ", request.args.get("id"))
    print("app: ", request.args.get("app"))
    print("appname: ", request.args.get("appname"))
    print("time: ", request.args.get("time"))
    print("usrargs: ", request.args.get("usrargs"))
    """
    topic = request.args.get("id") + "/cm/nodes"

    if request.args.get("action") == "publish":
        _mqtt_publish(topic, "publish")
    elif request.args.get("action") == "publish_done":
        _mqtt_publish(topic, "publish_done")

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)