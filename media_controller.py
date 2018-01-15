from p2p_mqtt.p2p_mqtt import P2PMqtt
from db.collection_online import CollectionOnLine
import logging.config

# topic format: dest_tag/source_tag/_TOPIC_XXX
_CONTROLLER_TAG = "media_controller"

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


def _parse_source_tag(source_id):
    if True:
        vid, gid, nid = source_id.split('_')
    else:
        source_tag_split = source_id.split('_')
        vid = source_tag_split[0]
        gid = source_tag_split[1]
        nid = "%s_%s" % (source_tag_split[2], source_tag_split[3])

    # code block will not introduce new scope,
    # which is not the same as C/CPP
    return vid, gid, nid


def _publish_one_pusher_to_all(source_tag, add_remove_update, node_info=None):
    vid, gid, nid = _parse_source_tag(source_tag)

    if node_info is None:
        node_info = _col_online.find_one({"id": nid})
        if node_info is None:
            logger_mc.debug("publish one pusher failed!")
            return

    if node_info['role'] != _ROLE_PUSHER:
        return

    to_who = "%s_%s_*" % (vid, _ROLE_PULLER)
    payload = '{"%s":[%s]}' % (add_remove_update, node_info)
    _p2pc.mqtt_publish("%s/%s/%s" % (to_who, _CONTROLLER_TAG, _TOPIC_NODES_CHANGE),
                       payload, qos=2, retain=False)


def _publish_all_pusher_to_one(source_tag):
    role_info = _col_online.find_role(role=_ROLE_PUSHER)
    payload = '{"%s": %s}' % (_CHANGE_ALL_ONLINE, role_info)
    _p2pc.mqtt_publish("%s/%s/%s" % (source_tag, _CONTROLLER_TAG, _TOPIC_NODES_CHANGE),
                       payload, qos=2, retain=False)


def handle_online(source_tag, method_params):
    """
    mehtod: online
    params: {k:v, ...}
    """
    logger_mc.debug("@handle_online")

    if not isinstance(method_params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    vid, gid, nid = _parse_source_tag(source_tag)

    _col_online.online(nid, method_params)

    role = method_params['role']
    if role == _ROLE_PULLER:
        _publish_all_pusher_to_one(source_tag)
    elif role == _ROLE_PUSHER:
        _publish_one_pusher_to_all(source_tag, _CHANGE_NEW_ONLINE, method_params)

    return "OK"


def handle_offline(source_tag, method_params):
    """
    mehtod: offline
    params: null
    """
    logger_mc.info("@handle offline")

    vid, gid, nid = _parse_source_tag(source_tag)
    node_info = _col_online.find_one({"id": nid})
    _col_online.offline(nid)

    if node_info is not None:
        # stupid to get the role in such an inefficient way
        node_role = node_info['role']
        if node_role == _ROLE_PUSHER:
            _publish_one_pusher_to_all(source_tag, _CHANGE_NEW_OFFLINE, node_info)

    return "OK"


def handle_update_field(source_id, method_params):
    if not isinstance(method_params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    vid, gid, nid = _parse_source_tag(source_id)

    _col_online.update(nid, method_params['field'], method_params['value'])

    _publish_one_pusher_to_all(source_id, _CHANGE_NEW_UPDATE, None)

    return "OK"


def hook_4_start_push_media(fsession):
    """
    :param msg:  method's parameters
    :return:
        True: the request will be forward
        False: the request failed directly, and reply ERROR
    """
    # TODO: check permission
    # TODO: check the status is publish or not
    # add url to the forward payload
    fsession.payload["params"]["url"] = fsession.push_url_rtmp
    return True


def hook_4_start_push_media_reply(fsession, reply_result):
    if reply_result == "OK":
        final_result = "{'url':'%s'}" % fsession.pull_url_rtmp
        return fsession.async_reply('publish', final_result)
    else:
        return fsession.sync_reply(reply_result)


def hook_4_stop_push_media(fsession):
    print("hook_4_stop_push_media")
    # check the count filed to determine whether forward is needed
    #
    return True


def handle_nodes_will(mqtt_msg):
    logger_mc.debug('@handle_nodes_will')
    print(repr(mqtt_msg))
    nid = str(mqtt_msg.payload, encoding="utf-8")
    result = _col_online.find_one({"id": nid})
    if result is not None:
        _col_online.remove(nid)
        role = result['role']
        if role == _ROLE_PUSHER:
            _publish_one_pusher_to_all("%s_%s_%s" % (result['vendor_id'], result['group_id'], nid),
                                       _CHANGE_NEW_OFFLINE, result)
    else:
        print("can not find %s" % nid)


def handle_ali_notify(mqtt_msg):
    logger_mc.info("handle_ali_notify")
    print(repr(mqtt_msg))

    payload = eval(mqtt_msg.payload)
    status = payload["action"]
    node_tag = payload["app"]
    vid, gid, nid = node_tag.split('_')
    _col_online.update(nid, "stream_status", status)

    stag = "%s/%s" % (node_tag, status)
    _p2pc._session_manager.signal(stag)
    #_publish_one_pusher_to_all(node_tag, _CHANGE_NEW_UPDATE, None)


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger_mc = logging.getLogger(__name__)

    _p2pc = P2PMqtt(broker_url="139.224.128.15", whoami=_CONTROLLER_TAG)
    _p2pc.register_rpc_handler(_REQUEST_ONLINE, handle_online)
    _p2pc.register_rpc_handler(_REQUEST_OFFLINE, handle_offline)
    _p2pc.register_rpc_handler(_REQUEST_UPDATE_FIELD, handle_update_field)

    # media_controller/broker/nodes_will
    _p2pc.register_topic_handler('nodes_will/+', handle_nodes_will)
    _p2pc.register_topic_handler("media_controller/ali/notify", handle_ali_notify)

    _p2pc.register_forward_request_hook(_REQUEST_START_PUSH_MEDIA, hook_4_start_push_media)
    _p2pc.register_forward_reply_hook(_REQUEST_START_PUSH_MEDIA, hook_4_start_push_media_reply)

    _p2pc.register_forward_request_hook(_REQUEST_STOP_PUSH_MEDIA, hook_4_stop_push_media)

    _p2pc.loop()


