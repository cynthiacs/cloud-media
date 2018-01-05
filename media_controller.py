from p2p_mqtt.p2p_mqtt import P2PMqtt
from db.collection_online import CollectionOnLine
import logging.config

_CONTROLLER_ID = "media_controller"

# topics: towho/fromwho/_TOPIC_XXX
_TOPIC_REQUEST = 'request'
_TOPIC_REPLY = 'reply'
_TOPIC_NODES_CHANGE = 'nodes_change'
_TOPIC_EXCHANGE_MSG = 'exchange_msg'

# RPC requests
_REQUEST_ONLINE = 'Online'
_REQUEST_OFFLINE = 'Offline'
_REQUEST_UPDATE_FIELD = 'UpdateField'
_REQUEST_START_PUSH_MEDIA = 'StartPushMedia'
_REQUEST_STOP_PUSH_MEDIA = 'StopPushMedia'
# old definition, use DB proxy in some of the RPCs
# _REQUEST_NODES_UPDATE = 'nodes_update'
# _REQUEST_NODES_FIND = 'nodes_find'

# node's change for _TOPIC_NODES_CHANGE
_CHANGE_ALL_ONLINE = "all_online"
_CHANGE_NEW_ONLINE = "new_online"
_CHANGE_NEW_OFFLINE = "new_offline"
_CHANGE_NEW_UPDATE = "new_update"

# CM stream status
_NODE_STATUS_PUSHING = 'pushing'
_NODE_STATUS_PUSHING_CLOSE = 'pushing_close'
_NODE_STATUS_PULLING = 'pulling'
_NODE_STATUS_PULLING_CLOSE = 'pulling_close'
_NODE_STATUS_UNKNOWN = 'unknown'

_NODE_GROUPID_DEFAULT = "00000000";
_NODE_GROUPNICK_DEFAULT = "Default Group";
_NODE_VENDORID_DEFAULT = "00000000";
_NODE_VENDORNICK_DEFAULT = "CM Team";

# node's role
_ROLE_ALL = "all"
_ROLE_PULLER = 'puller'
_ROLE_PUSHER = 'pusher'
_ROLE_MC = "media_controller"
_ROLE_TEST = "tester"

# global module objects
_p2pc = None
_col_online = CollectionOnLine()


def _publish_one_pusher(source_id, add_remove_update):
    source_tag_split = source_id.split('_')
    vid = source_tag_split[0]
    gid = source_tag_split[1]
    nid = source_tag_split[2]

    to_who = "%s_%s_*" % (vid, _ROLE_PULLER)
    payload = '{"%s":[{"id":%s}]}' % (add_remove_update, source_id)
    _p2pc.mqtt_publish("%s/%s/%s" % (to_who, _CONTROLLER_ID, _TOPIC_NODES_CHANGE),
                       payload, qos=2, retain=False)


def _publish_all_pusher(source_id):
    role_info = _col_online.find_role(role=_ROLE_PUSHER)
    payload = '{"%s": %s}' % (_CHANGE_ALL_ONLINE, role_info)
    _p2pc.mqtt_publish("%s/%s/%s" % (source_id, _CONTROLLER_ID, _TOPIC_NODES_CHANGE),
                       payload, qos=2, retain=False)


def handle_online(source_id, params):
    """
    mehtod: online
    params: {k:v, ...}
    """
    logger_mc.debug("@handle_online")

    if not isinstance(params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    _col_online.online(source_id, params)

    role = params['role']
    if role == _ROLE_PULLER:
        _publish_all_pusher(source_id)
    elif role == _ROLE_PUSHER:
        _publish_one_pusher(source_id, _CHANGE_NEW_ONLINE)

    return "OK"


def handle_offline(source_id, params):
    """
    mehtod: offline
    params: null
    """
    logger_mc.info("@handle offline")

    _col_online.offline(source_id)
    source_tag_split = source_id.split('_')
    vid = source_tag_split[0]
    # gid = source_tag_split[1]
    nid = source_tag_split[2]

    node_info = _col_online.find_one({"id": nid})
    if node_info is not None:
        # stupid to get the role in such an inefficient way
        node_role = node_info['role']
        if node_role == _ROLE_PUSHER:
            _publish_one_pusher(source_id, _CHANGE_NEW_OFFLINE)

    return "OK"


def handle_update_field(source_id, rpc_params):
    source_tag_split = source_id.split('_')
    vid = source_tag_split[0]
    gid = source_tag_split[1]
    nid = source_tag_split[2]

    params = eval(rpc_params)
    _col_online.update(nid, params['field'], params['value'])

    node_info = _col_online.find_one({"id": nid})
    if node_info is not None:
        if node_info['role'] == _ROLE_PUSHER:
            _publish_one_pusher(source_id, _CHANGE_NEW_UPDATE)

    return "OK"


def handle_nodes_will(msg):
    logger_mc.debug('@handle_nodes_will')
    print(repr(msg))
    nid = str(msg.payload, encoding="utf-8")
    result = _col_online.find_one({"id": nid})
    if result is not None:
        _col_online.remove(nid)
        role = result['role']
        if role == _ROLE_PUSHER:
            _publish_one_pusher("%s_%s_%s" % (result['vendor_id'], result['group_id'], nid),
                                _CHANGE_NEW_OFFLINE)


def hook_4_start_push_media(msg):
    """
    :param msg:  method's parameters
    :return:
        True: the request will be forward
        False: the request failed directly, and reply ERROR
    """
    print(repr(msg))
    return True


def hook_4_stop_push_media(msg):
    print(repr(msg))
    return True


def handle_ali_notify(msg):
    logger_mc.info("handle_ali_notify")
    print(repr(msg))
    role = _ROLE_PUSHER
    print("publish all " + role + " 's info")
    role_info = _col_online.find_role(role=role)
    print("\t %s" % role_info)
    to_who = "%s_%s_%s" % (_NODE_VENDORID_DEFAULT, _NODE_GROUPID_DEFAULT, _TOPIC_NODES_CHANGE)
    _p2pc.mqtt_publish("%s/%s/%s" % (to_who, _CONTROLLER_ID, _TOPIC_NODES_CHANGE), role_info, qos=2, retain=False)


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger_mc = logging.getLogger(__name__)

    _p2pc = P2PMqtt(broker_url="139.224.128.15", whoami=_CONTROLLER_ID)
    _p2pc.register_rpc_handler(_REQUEST_ONLINE, handle_online)
    _p2pc.register_rpc_handler(_REQUEST_OFFLINE, handle_offline)
    #_p2pc.register_rpc_handler(_REQUEST_UPDATE_FIELD, handle_update_field)

    _p2pc.register_topic_handler('nodes_will/+', handle_nodes_will)

    _p2pc.register_forward_request_hook(_REQUEST_START_PUSH_MEDIA, hook_4_start_push_media)
    _p2pc.register_forward_request_hook(_REQUEST_STOP_PUSH_MEDIA, hook_4_stop_push_media)

    #p2pc.register_topic_handler("controller/ali/notify", handle_ali_notify)
    _p2pc.loop()


