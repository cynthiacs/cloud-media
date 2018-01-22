from p2p_mqtt.p2p_mqtt import P2PMqtt
import logging.config
from db.collection_online import OnlineNodes
import time
from stream_cookie import StreamCookie

# topic format: dest_tag/source_tag/_TOPIC_XXX
CONTROLLER_TAG = "media_controller"

_TOPIC_REQUEST = 'request'
_TOPIC_REPLY = 'reply'
_TOPIC_NODES_CHANGE = 'nodes_change'
_TOPIC_EXCHANGE_MSG = 'exchange_msg'
_TOPIC_STREAM_EXCEPTION = 'stream_exception'

# RPC requests
REQUEST_ONLINE = 'Online'
REQUEST_OFFLINE = 'Offline'
REQUEST_UPDATE_FIELD = 'UpdateField'
REQUEST_START_PUSH_MEDIA = 'StartPushMedia'
REQUEST_STOP_PUSH_MEDIA = 'StopPushMedia'
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
_NODE_STATUS_PUSHING_ERROR = 'pushing_error'
_NODE_STATUS_PULLING = 'pulling'
_NODE_STATUS_PULLING_CLOSE = 'pulling_close'
_NODE_STATUS_PULLING_ERROR = 'pulling_error'
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

logging.config.fileConfig('logging.conf')
logger_mc = logging.getLogger(__name__)

media_controller = P2PMqtt(broker_url="139.224.128.15", whoami=CONTROLLER_TAG)
online_nodes = OnlineNodes()
stream_cookie = StreamCookie(logger_mc)   # scattergun, bad practice


def _parse_node_tag(source_id):
    return source_id.split('_')


def _publish_one_pusher_to_all(source_tag, add_remove_update, node_info=None):
    vid, gid, nid = _parse_node_tag(source_tag)

    if node_info is None:
        node_info = online_nodes.find_one(source_tag)

        if node_info is None:
            logger_mc.debug("publish one pusher failed!")
            return

    if node_info['role'] != _ROLE_PUSHER:
        return

    to_who = "%s_%s_*" % (vid, _ROLE_PULLER)
    payload = '{"%s":[%s]}' % (add_remove_update, node_info)
    media_controller.publish("%s/%s/%s" % (to_who, CONTROLLER_TAG, _TOPIC_NODES_CHANGE),
                             payload, qos=2, retain=False)


def _publish_all_pusher_to_one(source_tag):
    role_info = online_nodes.find_role(source_tag, _ROLE_PUSHER)

    payload = '{"%s": %s}' % (_CHANGE_ALL_ONLINE, role_info)
    media_controller.publish("%s/%s/%s" % (source_tag, CONTROLLER_TAG, _TOPIC_NODES_CHANGE),
                             payload, qos=2, retain=False)


@media_controller.rpc_handler(REQUEST_ONLINE)
def handle_online(source_tag, method_params):
    """
    mehtod: online
    params: {k:v, ...}
    """
    logger_mc.debug("@handle_online")

    if not isinstance(method_params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    online_nodes.remove(source_tag)
    online_nodes.insert(source_tag, document=method_params)

    role = method_params['role']
    if role == _ROLE_PULLER:
        _publish_all_pusher_to_one(source_tag)
    elif role == _ROLE_PUSHER:
        _publish_one_pusher_to_all(source_tag, _CHANGE_NEW_ONLINE, method_params)

    return "OK"


@media_controller.rpc_handler(REQUEST_OFFLINE)
def handle_offline(source_tag, method_params):
    """
    mehtod: offline
    params: null
    """
    logger_mc.info("@handle offline")

    node_info = online_nodes.find_one(source_tag)
    online_nodes.remove(source_tag)
    if node_info is not None:
        # stupid to get the role in such an inefficient way
        logger_mc.debug(node_info)
        node_role = node_info['role']
        if node_role == _ROLE_PUSHER:
            _publish_one_pusher_to_all(source_tag, _CHANGE_NEW_OFFLINE, node_info)
            stream_cookie.clean_pusher(source_tag)
        elif node_role == _ROLE_PULLER:
            stream_cookie.clean_puller(source_tag)

    return "OK"


@media_controller.rpc_handler(REQUEST_UPDATE_FIELD)
def handle_update_field(source_tag, method_params):
    if not isinstance(method_params, dict):
        logger_mc.error("online: params format is incorrect.")
        return "ERROR"

    online_nodes.update(source_tag, method_params['field'], method_params['value'])
    _publish_one_pusher_to_all(source_tag, _CHANGE_NEW_UPDATE, None)
    if method_params['field'] == 'stream_status' \
            and method_params['value'] == _NODE_STATUS_PUSHING_ERROR:
        # loop to notify the pullers is ineffecient.
        # better to let pullers to subscribe a specific topic for each pusher
        for puller_tag in stream_cookie.get_pullers(source_tag):
            topic = "%s/%s/%s" % (puller_tag, CONTROLLER_TAG, _TOPIC_STREAM_EXCEPTION)
            payload = {"stream_exception": "pusher_error"}
            media_controller.publish(topic, str(payload), qos=2)

    return "OK"


@media_controller.forward_request_hook(REQUEST_START_PUSH_MEDIA)
def hook_4_start_push_media(fsession):
    """
    :param fsession:  forward session
    :return:
        True: the request will be forward
        False: the request needn't forward
    """
    # TODO: check permission
    target_node_tag = fsession._dest_tag
    vid, gid, nid = _parse_node_tag(target_node_tag)
    result = online_nodes.find_one(target_node_tag)
    if result is None:
        fsession.sync_reply("Error: nid:%s is not online" % nid)
        return False

    stream_status = result['stream_status']
    if stream_status == 'publish' or stream_status == 'pushing':
        logger_mc.debug("%s is %s, so no need forward request anymore" %
                        (target_node_tag, stream_status))

        if stream_status == 'pushing':
            logger_mc.warning("temp workaround, async reply to be done!")
            time.sleep(1)
            # fsession.async_reply('publish', final_result)

        reply_payload = "{'url':'%s'}" % fsession.pull_url_rtmp
        fsession.sync_reply(reply_payload)

        stream_cookie.join_stream(fsession.stream_tag, fsession._source_tag)
        return False

    # add url to the forward payload
    fsession.payload["params"]["url"] = fsession.push_url_rtmp
    return True


@media_controller.forward_reply_hook(REQUEST_START_PUSH_MEDIA)
def hook_4_start_push_media_reply(fsession, reply_result):
    """
    :param fsession: forward session
    :param reply_result: the reply from media pusher
    :return:
        fsession.async_reply('publish', final_result)
            waiting signal 'publish' and then send final_result
        fsession.sync_reply(reply_result)
            send reply result
    """
    if reply_result == "OK":
        stream_cookie.join_stream(fsession.stream_tag, fsession._source_tag)

        final_result = "{'url':'%s'}" % fsession.pull_url_rtmp
        return fsession.async_reply('publish', final_result)
    else:
        return fsession.sync_reply(reply_result)


@media_controller.forward_request_hook(REQUEST_STOP_PUSH_MEDIA)
def hook_4_stop_push_media(fsession):
    """
    :param fsession:  forward session
    :return:
        True: the request will be forward
        False: the request needn't forward
    """
    logger_mc.debug("hook_4_stop_push_media")

    target_node_tag = fsession._dest_tag
    vid, gid, nid = _parse_node_tag(target_node_tag)
    result = online_nodes.find_one(target_node_tag)
    if result is None:
        fsession.sync_reply("Error: nid:%s is not online" % nid)
        return False

    stream_cookie.quit_stream(fsession.stream_tag, fsession._source_tag)

    if stream_cookie.count_puller(fsession.stream_tag) == 0:
        logger_mc.info("forward stop_push_media command to %s" % target_node_tag)
        return True
    else:
        fsession.sync_reply("OK")
        return False


@media_controller.topic_handler("cm/nodes_will")
def handle_nodes_will(mqtt_msg):
    logger_mc.debug('@handle_nodes_will')
    logger_mc.debug(repr(mqtt_msg))
    node_tag = str(mqtt_msg.payload, encoding="utf-8")
    result = online_nodes.find_one(node_tag)
    if result is not None:
        online_nodes.remove(node_tag)
        role = result['role']
        if role == _ROLE_PUSHER:
            _publish_one_pusher_to_all(node_tag, _CHANGE_NEW_OFFLINE, result)
            stream_cookie.clean_pusher(node_tag)
        elif role == _ROLE_PULLER:
            stream_cookie.clean_puller(node_tag)
    else:
        logger_mc.warning("can not find %s" % node_tag)


@media_controller.topic_handler("media_controller/ali/notify")
def handle_ali_notify(mqtt_msg):
    logger_mc.info("handle_ali_notify")
    logger_mc.debug(repr(mqtt_msg))

    payload = eval(mqtt_msg.payload)
    status = payload["action"]
    app = payload["app"]
    stream = payload["stream"]
    node_tag = app  # TODO: change it
    online_nodes.update(node_tag, "stream_status", status)

    if status == 'publish_done':
        stream_tag = "%s/%s" % (node_tag, stream)
        for puller_tag in stream_cookie.get_pullers(node_tag):
            pass
            # topic = "%s/%s/%s" % (puller_tag, CONTROLLER_TAG, _TOPIC_STREAM_EXCEPTION)
            # payload = {"stream_exception": "pusher_error"}
            # media_controller.publish(topic, str(payload), qos=2)

        stream_cookie.del_stream(stream_tag)

    stag = "%s/%s" % (node_tag, status)
    media_controller.signal(stag)


if __name__ == '__main__':
    media_controller.run()


