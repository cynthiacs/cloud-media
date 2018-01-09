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
    infot = mqttc.publish(topic, payload, qos=2, retain=True)
    infot.wait_for_publish()


class CollectionOnLine(object):
    def __init__(self, url='mongodb://139.224.128.15'):
        self._db_client = MongoClient(url)
        self._db = self._db_client.extmqtt_nodes
        self._db_col_nodes_online = self._db.nodes_online

    def remove(self, whoami):
        if self._db_col_nodes_online.find_one({'whoami': whoami}) is not None:
            print("remove: " + whoami)
            self._db_col_nodes_online.remove({'whoami': whoami})

    def insert(self, params):
        self._db_col_nodes_online.insert_one(params)

    def find_all(self):
        nodes_online = self._db_col_nodes_online.find()
        # NOTE: this works, but str(list(car_online)) wont
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find_role(self, role):
        nodes_online = self._db_col_nodes_online.find({"role": role})
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find(self, filter_param):
        """
        :param filter_param:
        :return: string to transfer by mqtt
        """
        # find return Cursor instance which can be interate over all mathing document
        find_result = self._db_col_nodes_online.find(filter_param)
        # convert into list, take care about the memory when using this !!
        l_find_result = list(find_result)
        return str(l_find_result)

    def find_one(self, filter_param):
        """
        :param filter_param:
        :return:  return the first match, and the result is dict
        """
        return self._db_col_nodes_online.find_one(filter_param)

    def update(self, whoami, filed, value):
        print("update " + whoami)
        print("\t(" + filed + ":" + value + ")")
        self._db_col_nodes_online.update_one({"whoami": whoami}, {'$set': {filed: value}})


_online_col = CollectionOnLine()

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

    #topic = request.args.get("id") + "/cm/nodes"
    #action = request.args.get("action")
    #if action is not None:
    #    _mqtt_publish(topic, action)

    action = request.args.get("action")
    app_name = request.args.get("appname")
    stream_name = request.args.get("id")

    # let controller do this  ...
    #vid, gid, nid = app_name.split('_')
    #_online_col.update(nid, "status", action)

    payload = '{"action": %s, "app": %s, "stream": %s}' % (action, app_name, stream_name)
    _mqtt_publish("media_controller/ali/notify", payload)

    """
    node_id = request.args.get("id")
    status = request.args.get("action")
    _online_col.update(node_id, "status", status)

    _mqtt_publish("controller/ali/notify", "streams_notify")
    """

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)