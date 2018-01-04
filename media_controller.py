from pymongo import MongoClient
from p2p_mqtt.p2p_mqtt import P2PMqtt
import logging
import logging.config

_CONTROLLER_ID = "media_controller"
_REQUEST_ONLINE = 'Online'
_REQUEST_OFFLINE = 'Offline'

_TOPIC_NODES_CHANGE = 'nodes_change'  # towho/fromwho/nodes_change
_CHANGE_ALL_ONLINE = "all_online";
_CHANGE_NEW_ONLINE = "new_online";
_CHANGE_NEW_OFFLINE = "new_offline";
_CHANGE_NEW_UPDATE = "new_update";


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

    def remove(self, node_id):
        if self._db_col_nodes_online.find_one({'id': node_id}) is not None:
            print("[DB] remove: " + node_id)
            self._db_col_nodes_online.remove({'id': node_id})

    def insert(self, params):
        print("[DB] insert %s" % params)
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

    def update(self, node_id, filed, value):
        print("[DB] update " + node_id)
        print("\t(" + filed + ":" + value + ")")
        self._db_col_nodes_online.update_one({"id": node_id}, {'$set': {filed: value}})

    def online(self, node_id, params):
        print("[DB] online:" + node_id)
        self.remove(node_id)
        self.insert(params=params)

    def offline(self, node_id):
        print("[DB] offline:" + node_id)
        self.remove(node_id)


_online_col = CollectionOnLine()


def publish_role(role):
    print("publish all " + role + " 's info")
    role_info = _online_col.find_role(role=role)
    print("\t %s" % role_info)
    p2pc.mqtt_publish(role + _TOPIC_NODES_ON_LINE, role_info, qos=2, retain=True)


def handle_online(source_id, params):
    """
    mehtod: online
    params: {k:v, ...}
    """
    logger_mc.info("@handle_online")

    if not isinstance(params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    role = params['role']
    print(repr(params))

    _online_col.online(source_id, params)

    if role == 'puller':
        print("publish all role:%s 's info to node:%s" % (role, source_id))
        role_info = _online_col.find_role(role='pusher')
        print("\t all role: \n\t %s" % role_info)
        payload = '{"%s": %s}' % (_CHANGE_ALL_ONLINE, role_info)
        p2pc.mqtt_publish("%s/%s/%s" % (source_id, _CONTROLLER_ID, _TOPIC_NODES_CHANGE), payload, qos=2, retain=True)
    elif role == 'pusher':
        source_tag_split = source_id.split('_')
        vid = source_tag_split[0]
        to_who = "%s_puller_*" % vid
        payload = '"%s":[%s]' % (_CHANGE_NEW_ONLINE, params)
        p2pc.mqtt_publish("%s/%s/%s" % (to_who, _CONTROLLER_ID, _TOPIC_NODES_CHANGE), payload, qos=2, retain=True)

    return "OK"


def handle_offline(source_id, params):
    """
    mehtod: offline
    params: null
    """
    logger_mc.info("@handle offline")

    _online_col.offline(source_id)
    source_tag_split = source_id.split('_')
    vid = source_tag_split[0]
    # gid = source_tag_split[1]
    # nid = source_tag_split[2]
    to_who = "%s_puller_*" % vid
    payload = '{"%s":[{"id":%s}]}' % (_CHANGE_NEW_OFFLINE, source_id)
    p2pc.mqtt_publish("%s/%s/%s" % (to_who, _CONTROLLER_ID, _TOPIC_NODES_CHANGE), payload, qos=2, retain=True)

    return "OK"


def handle_nodes_find(rpc_params):
    params = eval(rpc_params)
    return _online_col.find(params)


def handle_nodes_update(rpc_params):
    params = eval(rpc_params)
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


def hook_4_hello(msg):
    """
    :param msg:  method hello's parameters
    :return:
        True: the reqeust hello will be forward
        False: the request failed directly, and reply ERROR
    """
    logger_mc.info("handle_ali_notify")
    print(repr(msg))
    return True


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger_mc = logging.getLogger(__name__)

    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami=_CONTROLLER_ID)
    p2pc.register_rpc_handler(_REQUEST_ONLINE, handle_online)
    p2pc.register_rpc_handler(_REQUEST_OFFLINE, handle_offline)
    #p2pc.register_rpc_handler(_REQUEST_NODES_UPDATE, handle_nodes_update)
    #p2pc.register_rpc_handler(_REQUEST_NODES_FIND, handle_nodes_find)

    #p2pc.register_topic_handler(_TOPIC_NODES_WILL, handle_nodes_will)
    #p2pc.register_topic_handler("controller/ali/notify", handle_ali_notify)

    #p2pc.register_forward_request_hook("hello", hook_4_hello)
    p2pc.loop()


