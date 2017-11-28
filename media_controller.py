from pymongo import MongoClient
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger

_REQUEST_ONLINE = 'online'
_REQUEST_OFFLINE = 'offline'
_REQUEST_NODES_UPDATE = 'nodes_update'
_REQUEST_NODES_FIND = 'nodes_find'

_TOPIC_NODES_WILL = 'cm/nodes_will/+'
_TOPIC_NODES_ON_LINE = '/nodes_online/cm'  # role +
# id/role/nodes_update/cm

p2pc = None


class CollectionOnLine(object):
    def __init__(self, url='mongodb://139.224.128.15'):
        self._db_client = MongoClient(url)
        self._db = self._db_client.extmqtt_nodes
        self._db_col_nodes_online = self._db.nodes_online

    def remove(self, whoami):
        if self._db_col_nodes_online.find_one({'whoami': whoami}) is not None:
            print("already in online, so i remove it and re-Online")
            self._db_col_nodes_online.remove({'whoami': whoami})

    def insert(self, params):
        self._db_col_nodes_online.insert_one(params)

    def find_all(self):
        nodes_online = self._db_col_nodes_online.find()
        # update retain topic
        # NOTE: this works!, but str(list(car_online)) wont
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find_role(self, role):
        nodes_online = self._db_col_nodes_online.find({"role": role})
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find(self, filter_param):
        find_result = self._db_col_nodes_online.find(filter_param)
        l_find_result = list(find_result)
        return str(l_find_result)

    def update(self, whoami, filed, value):
        print("update " + whoami)
        print("\t(" + filed + ":" + value + ")")
        self._db_col_nodes_online.update_one({"whoami": whoami}, {'$set': {filed: value}})

    def publish(self, p2p_client):
        print("\t  " + self.find_all())
        p2p_client.mqtt_publish("all" + _TOPIC_NODES_ON_LINE, self.find_all(), qos=2, retain=True)

    def online(self, whoami, params):
        print("online:" + whoami)
        self.remove(whoami)
        self.insert(params=params)

    def offline(self, whoami):
        print("offline:" + whoami)
        self.remove(whoami)


_online_col = CollectionOnLine()


def handle_online(jrpc):
    """
    mehtod: online
    params: {
        whoami: my id
        time: the time to send online request
        location: longi and lati tude
    }
    """
    print(repr(jrpc))
    params = jrpc['params']
    whoami = params['whoami']
    role = params['role']
    _online_col.online(whoami, params)

    p2pc.mqtt_publish(role + _TOPIC_NODES_ON_LINE, _online_col.find_role(role=role), qos=2, retain=True)
    return "OK"


def handle_offline(jrpc):
    """
    mehtod: offline
    params: {
        whoami: my id
        time: the time to send online request
        location: longi and lati tude
    }
    """
    print(repr(jrpc))
    params = jrpc['params']
    whoami = params['whoami']
    role = params['role']
    _online_col.offline(whoami)

    p2pc.mqtt_publish(role + _TOPIC_NODES_ON_LINE, _online_col.find_role(role=role), qos=2, retain=True)
    return "OK"


def handle_nodes_update(jrpc):
    params = jrpc['params']
    _online_col.update(params['whoami'], params['field'], params['value'])
    return "OK"


def handle_nodes_find(jrpc):
    params = jrpc['params']
    return _online_col.find(params)


def handle_nodes_will(msg):
    print("will !!!!!!!!!!!!!!!!")
    print(repr(msg))
    whoami = msg.paylaod
    _online_col.offline(p2pc, whoami)
    # p2pc.mqtt_publish(role + _TOPIC_NODES_ON_LINE, _online_col.find_role(role=role), qos=2, retain=True)
    pass


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='controller')
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_online)
    p2pc.register_request_handler(_REQUEST_OFFLINE, handle_offline)
    p2pc.register_request_handler(_REQUEST_NODES_UPDATE, handle_nodes_update)
    p2pc.register_request_handler(_REQUEST_NODES_FIND, handle_nodes_find)

    p2pc.register_topic_handler(_TOPIC_NODES_WILL, handle_nodes_will)
    p2pc.loop()


