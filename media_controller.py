from pymongo import MongoClient
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger
import logging
import logging.config

_REQUEST_ONLINE = 'online'
_REQUEST_OFFLINE = 'offline'
_REQUEST_NODES_UPDATE = 'nodes_update'
_REQUEST_NODES_FIND = 'nodes_find'

_TOPIC_NODES_WILL = 'cm/nodes_will'  # /+
_TOPIC_NODES_ON_LINE = '/nodes_online/cm'  # role +

p2pc = None


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

    def online(self, whoami, params):
        print("online:" + whoami)
        self.remove(whoami)
        self.insert(params=params)

    def offline(self, whoami):
        print("offline:" + whoami)
        self.remove(whoami)


_online_col = CollectionOnLine()


def publish_role(role):
    print("publish all " + role + " 's info")
    p2pc.mqtt_publish(role + _TOPIC_NODES_ON_LINE, _online_col.find_role(role=role), qos=2, retain=True)


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

    publish_role(role)
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

    publish_role(role)
    return "OK"


def handle_nodes_find(jrpc):
    params = jrpc['params']
    return _online_col.find(params)


def handle_nodes_update(jrpc):
    params = jrpc['params']
    _online_col.update(params['whoami'], params['field'], params['value'])

    # NOTE: this is wasteful, we may only need to broadcast the specific node at all
    result = _online_col.find_one({"whoami": params['whoami']})
    if result and result['role'] is not None:
        publish_role(result['role'])

    return "OK"


def handle_nodes_will(msg):
    print(repr(msg))
    whoami = str(msg.payload, encoding="utf-8")
    print("!!! who's will: " + whoami)
    result = _online_col.find_one({"whoami": whoami})
    if result is not None:
        role = result['role']
        _online_col.remove(whoami)
        if role is not None:
            publish_role(role)


def handle_ali_notify(msg):
    logger_mc.info("handle_ali_notify")
    print(repr(msg))
    publish_role("pusher")


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger_mc = logging.getLogger(__name__)

    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='controller')
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_online)
    p2pc.register_request_handler(_REQUEST_OFFLINE, handle_offline)
    p2pc.register_request_handler(_REQUEST_NODES_UPDATE, handle_nodes_update)
    p2pc.register_request_handler(_REQUEST_NODES_FIND, handle_nodes_find)

    p2pc.register_topic_handler(_TOPIC_NODES_WILL, handle_nodes_will)
    p2pc.register_topic_handler("controller/ali/notify", handle_ali_notify)
    p2pc.loop()


