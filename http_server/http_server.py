from flask import Flask
from flask import request
import paho.mqtt.client as mqtt
from pymongo import MongoClient


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
    infot = mqttc.publish(topic, payload, qos=2, retain=False)
    infot.wait_for_publish()


@app.route('/cm_live_streams_notify')
def cm_live_streams_notify():
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
    action = request.args.get("action")
    ip = request.args.get("ip")
    stream = request.args.get("id")
    app = request.args.get("appname")
    appname = request.args.get("appname")
    time = request.args.get("time")
    userargs = request.args.get("usrargs")


    payload = "{'action': '%s', 'ip': '%s', 'stream': '%s', 'app': '%s', \
                'appname':'%s', 'time':'%s', 'userargs':'%s'}" \
                % (action, ip, stream, app, appname, time, userargs)

    print("@cm_live_streams_notify payload: %s" % payload)
    _mqtt_publish("media_controller/ali/notify", payload)

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)
