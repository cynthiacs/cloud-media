"""
Extended MQTT module to provide a P2P message feature.
"""
import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub
import logging
import hashlib
import re
import time
import json
from .config import config

__all__ = ('P2PMqtt', 'ForwardSession',)
logger = logging.getLogger(__name__)


class ExtMqttContext(object):
    def __init__(self):
        self._mqtt_client = None
        self._ext_mqtt_client = None
        self._p2p_mqtt_client = None

    @property
    def ext_mqtt_client(self):
        return self._ext_mqtt_client

    @ext_mqtt_client.setter
    def ext_mqtt_client(self, value):
        self._ext_mqtt_client = value


class ExtMqtt(mqtt.Client):
    def __init__(self, p2p_mqtt):
        # FIXME: loop reference
        self.p2p_mqtt = p2p_mqtt

        # the default parameters:
        # client_id = "", clean_session = True, userdata = None,
        # protocol = MQTTv311, transport = "tcp"
        super().__init__()

    def pub(self, topic, payload, qos=2, retain=False):
        logger.debug("publish \n\t %s \n\t %s \n\t %s \n\t %s" %
                     ("topic: " + str(topic),
                      "payload: " + str(payload),
                      "qos: " + str(qos),
                      "retain: " + str(retain)))
        self.publish(topic, payload, qos, retain)

    def sub(self, topic, qos=2):
        logger.debug("subscribe \n\t %s \n\t %s" %
                     ("topic: " + topic, "qos: " + str(qos)))
        self.subscribe(topic, qos)


class Session(object):
    def __init__(self, context, request_msg):
        # all session is created from mqtt request message
        self._context = context
        self._msg = request_msg

        # all request is json RPC format
        payload = eval(request_msg.payload)
        self.payload = payload
        self._method_name = payload['method']
        if 'params' in payload:
            self._method_params = payload['params']
        else:
            self._method_params = None
        self._method_id = payload['id']

    def send(self, topic, payload, qos=2, retain=False):
        self._context.ext_mqtt_client.pub(topic, payload, qos, retain)
        #self._context.ext_mqtt_client.publish(topic, payload, qos, retain)

    @staticmethod
    def make_session_tag_from_reply(mqtt_msg):
        topic_split = mqtt_msg.topic.split('/')
        _dest_id = topic_split[1]
        payload = eval(mqtt_msg.payload)
        return _dest_id + payload['id']

    @staticmethod
    def md5sum(src):
        m = hashlib.md5()
        m.update(src.encode("utf8"))
        return m.hexdigest()

    @staticmethod
    def get_auth_url(uri, exp, key="yangxudong"):
        p = re.compile("^(http://|https://|rtmp://)?([^/?]+)(/[^?]*)?(\\?.*)?$")
        if not p:
            return None
        m = p.match(uri)
        scheme, host, path, args = m.groups()
        if not scheme: scheme = "http://"
        if not path: path = "/"
        if not args: args = ""
        rand = "0"      # "0" by default, other value is ok
        uid = "0"       # "0" by default, other value is ok
        sstring = "%s-%s-%s-%s-%s" %(path, exp, rand, uid, key)
        hashvalue = Session.md5sum(sstring)
        auth_key = "%s-%s-%s-%s" %(exp, rand, uid, hashvalue)
        if args:
            return "%s%s%s%s&auth_key=%s" %(scheme, host, path, args, auth_key)
        else:
            return "%s%s%s%s?auth_key=%s" %(scheme, host, path, args, auth_key)


class RpcSession(Session):
    def __init__(self, context, mqtt_msg, reply_listener=None):
        Session.__init__(self, context, mqtt_msg)
        self._listener = reply_listener

        topic_split = self._msg.topic.split('/')
        self._dest_tag = topic_split[0]
        self._source_tag = topic_split[1]
        self.session_tag = self._dest_tag + self._method_id
        self.request_topic = "%s/%s/request" % (self._dest_tag, self._source_tag)
        self.reply_topic = "%s/%s/reply" % (self._source_tag, self._dest_tag)

    def send_request(self):
        topic = self.request_topic
        payload = self._msg.payload
        self.send(topic, payload)

    def call_listener(self, reply_msg):
        payload = eval(reply_msg.payload)
        result = payload['result']
        if self._listener is not None:
            self._listener(result)

    def send_reply(self, result):
        payload = '{"jsonrpc": "2.0", "result": "%s", "id": "%s"}' % (result, self._method_id)
        self.send(self.reply_topic, payload)


class ForwardSession(Session):
    def __init__(self, context, mqtt_msg):
        Session.__init__(self, context, mqtt_msg)

        topic_split = self._msg.topic.split('/')
        self._controller_tag = topic_split[0]
        self._source_tag = topic_split[1]

        if self._method_params is None:
            raise "forward session must contain target-id in rpc method params"

        if 'target-id' in self._method_params:
            self._dest_tag = self._method_params['target-id']
        else:
            print("error: no target-id")
            self._dest_tag = ""

        # self.session_tag = self._source_id + self._dest_id + self._method_id
        self.session_tag = self._dest_tag + self._method_id
        self.iport_request_topic = "%s/%s/request" % (self._controller_tag, self._source_tag)
        self.iport_reply_topic = "%s/%s/reply" % (self._source_tag, self._controller_tag)
        self.oport_request_topic = "%s/%s/request" % (self._dest_tag, self._controller_tag)
        self.oport_reply_topic = "%s/%s/reply" % (self._controller_tag, self._dest_tag)

        self.pull_url_base = config["PULL_BASE"]
        self.app_name = self._dest_tag
        vid, gid, nid = self._dest_tag.split('_')
        # self.stream_name = 'c1'
        self.stream_name = nid
        self.stream_tag = "%s/%s" % (self.app_name, self.stream_name)

        #expire_time = int(time.time()) + int(self.payload["params"]["expire-time"])
        expire_time = int(time.time()) + 100
        push_url_rtmp = "rtmp://video-center.alivecdn.com/%s/%s?vhost=%s" \
                        % (self.app_name, self.stream_name, config["PULL_BASE"])
        self.push_url_rtmp = Session.get_auth_url(push_url_rtmp, expire_time)
        pull_url_rtmp = "rtmp://%s/%s/%s" % (self.pull_url_base, self.app_name, self.stream_name)
        self.pull_url_rtmp = Session.get_auth_url(pull_url_rtmp, expire_time)
        pull_url_flv = "http://%s/%s/%s.flv" % (self.pull_url_base, self.app_name, self.stream_name)
        self.pull_url_flv = Session.get_auth_url(pull_url_flv, expire_time)
        pull_url_hls = "http://%s/%s/%s.m3u8" % (self.pull_url_base, self.app_name, self.stream_name)
        self.pull_url_hls = Session.get_auth_url(pull_url_hls, expire_time)

        if config["PULL_PROTOCOL"] == "RTMP":
            self.pull_url = self.pull_url_rtmp
        elif config["PULL_PROTOCOL"] == "HLS":
            self.pull_url = self.pull_url_hls
        elif config["PULL_PROTOCOL"] == "HTTP-FLV":
            self.pull_url = self.pull_url_flv
        else:
            logger.warning("config pull protocol is wrong")
            self.pull_url = self.pull_url_rtmp

        self.pending_replies = {}


    def send_request(self):
        topic = self.oport_request_topic
        self.send(topic, str(self.payload))

    def send_reply(self, result):
        topic = self.iport_reply_topic
        if result.startswith('{'):
            payload = '{"jsonrpc": "2.0", "result": %s, "id": "%s"}' % (result, self._method_id)
        else:
            payload = '{"jsonrpc": "2.0", "result": "%s", "id": "%s"}' % (result, self._method_id)
        self.send(topic, payload)

    def sync_reply(self, res):
        self.send_reply(res)
        return None

    def async_reply(self, action, final_result):
        signal_tag = "%s/%s" % (self._dest_tag, action)
        logger.debug("@async_reply sig_tag:" + signal_tag)

        def blocker(res):
            yield res
            self.send_reply(res)

        co = blocker(final_result)
        next(co)

        #self.pending_replies.setdefault(signal_tag,[])
        # only one corutine pending for one signal currently
        self.pending_replies[signal_tag] = co
        logger.debug("@async_reply install corutine for this fsession %s for signal %s " %
                        (self.session_tag, signal_tag))

        return signal_tag


class SessionManager(object):
    def __init__(self, context):
        self.context = context
        self._rpc_sessions = {}
        self._rpc_handler = {}

        self._forward_sessions = {}
        self._pending_sessions = []
        self._forward_request_hook = {}
        self._forward_reply_hook = {}
        self._jrpc_id = 0

    def send_rpc_request(self, dest_tag, source_tag, method, params, listener):
        msg = mqtt.MQTTMessage()
        topic = dest_tag + "/" + source_tag + "/request"
        msg.topic = topic.encode('utf-8')
        method_id = str(self._jrpc_id)
        msg.payload = '{"jsonrpc":"2.0", "method":"%s", "params":%s,"id":"%s"}' % (
                    method, params, method_id)

        self._jrpc_id += 1

        s = RpcSession(self.context, msg, listener)
        self._rpc_sessions[s.session_tag] = s
        s.send_request()

    def handle_request(self, iport_request_msg):
        logger.debug("handle_request")
        s = RpcSession(self.context, iport_request_msg)

        if s._method_name in self._rpc_handler:
            logger.debug("_rpc_handler: %s " %
                         self._rpc_handler[s._method_name].__name__)
            ret = self._rpc_handler[s._method_name](s._source_tag, s._method_params)
            s.send_reply(ret)
        elif s._method_name in self._forward_request_hook:
            logger.debug("_forward_handler")
            ss = ForwardSession(self.context, iport_request_msg)

            # ret: Ture, need forward; False, no need
            # stag: pending session with signal stag
            ret, stag = self._forward_request_hook[ss._method_name](ss)
            if ret:
                # add url to the forward payload
                ss.payload["params"]["url"] = ss.push_url_rtmp
 
                self._forward_sessions[ss.session_tag] = ss
                ss.send_request()
            else:
                if stag is not None:
                    logger.debug("@handle_request pending the session %s for signal: %s" %
                                     (ss.session_tag, stag))
                    self._pending_sessions.append(ss)
                else: 
                    logger.debug("no need to forward! do nothing at backgroud")
        else:
            logger.info("can not handle method: %s" % s._method_name)
            s.send_reply("ERROR: unknown method")

    def handle_reply(self, reply_msg):
        logger.debug("handle_reply")
        session_tag = Session.make_session_tag_from_reply(reply_msg)
        if session_tag in self._rpc_sessions:
            s = self._rpc_sessions[session_tag]
            s.call_listener(reply_msg)
            del self._rpc_sessions[session_tag]
        elif session_tag in self._forward_sessions:
            s = self._forward_sessions[session_tag]
            # reply hook has not implemented yet
            if s._method_name in self._forward_reply_hook:
                rpc = eval(reply_msg.payload)
                if 'result' not in rpc or 'id' not in rpc:
                    raise "reqeust's format is not correct"
                stag = self._forward_reply_hook[s._method_name](s, rpc['result'])
                if stag is not None:
                    logger.debug("pending the reply of session: %s" % session_tag)
                    self._pending_sessions.append(s)
            else:
                self._forward_sessions[session_tag].send_reply('OK')

            del self._forward_sessions[session_tag]
            logger.debug("@handle_oport_reply session:%s is deleted" % session_tag)
        else:
            logger.error("@handle_oport_reply session not found!")

    def signal(self, stag):
        """
        :param stag:   dest_tag/action
        :return:
        """
        logger.debug("@signal pending sessions tags:" + str([s.session_tag for s in self._pending_sessions]))

        for s in self._pending_sessions:
            if stag in s.pending_replies:
                print('pending replies for stag %s found in session %s' % (stag, s.session_tag))
                final_result = '{"url":"%s"}' % s.pull_url
                s.send_reply(final_result)

        self._pending_sessions = [s for s in self._pending_sessions if stag not in s.pending_replies]

        #for s in self._pending_sessions:
        #    logger.debug('@signal check _pending_sessions %s pending_replies:' % s.session_tag)
        #    if stag in s.pending_replies:
        #        try:
        #            logger.debug('@signal found pending replies')
        #            s.pending_replies[stag].send(None)
        #        except StopIteration:
        #            print("StopIteration")
        #        del s.pending_replies[stag]
        #        #if not bool(s.pending_replies):
        #        # self._pending_sessions.remove(s)
        #    else:
        #        logger.debug('stag %s is not found' % stag)
        #        print('pending reply stag is: ' + str([k for k in s.pending_replies]))

    def register_rpc_handler(self, method_name, handler):
        self._rpc_handler[method_name] = handler

    def register_forward_request_hook(self, method_name, hook):
        """
        :param hook:
            @handle_iport_request ret = _method_hook[s._method_name](s._method_params)
        :return:
        """
        self._forward_request_hook[method_name] = hook

    def register_forward_reply_hook(self, method_name, hook):
        self._forward_reply_hook[method_name] = hook

    def register_oport_reply_hook(self, id):
        pass


class P2PMqtt(object):
    """
    P2PMqtt supports request and response mode based on MQTT
    """
    def __init__(self, *, broker_url, whoami='media_controller'):
        self._broker_url = broker_url
        self._my_tag = whoami

        self._ext_mqttc = ExtMqtt(self)

        self.topic_handlers = {}
        self.action_handlers = {}

        self.context = ExtMqttContext()
        self.context.ext_mqtt_client = self._ext_mqttc

        self._session_manager = SessionManager(self.context)

    @staticmethod
    def _on_connect_wrapper(ext_mqttc, obj, flags, rc):
        logger.info("on_connect with rc: " + str(rc))
        payload = "media_controller: reset at " + time.asctime(time.localtime(time.time()))
        ext_mqttc.pub('*_*_*/media_controller/reset', json.dumps({'description': payload}))

    @staticmethod
    def _on_message_wrapper(ext_mqttc, obj, msg):
        ext_mqttc.p2p_mqtt._on_message(msg)

    def _on_message(self, msg):
        logger.debug("==> _on_message")
        logger.debug("\t topic: " + msg.topic)
        logger.debug("\t qos: " + str(msg.qos))
        logger.debug("\t payload" + str(msg.payload))

        # Type 1: special topic, handle it directly
        if msg.topic in self.topic_handlers:
            logger.debug("start handle topic")
            self.topic_handlers[msg.topic](msg)
            return

        #if topic_matches_sub('nodes_will/+', msg.topic):
        #    print("this is a nodes will")

        topic_split = msg.topic.split('/')
        if topic_split[0] == 'nodes_will':
            self.topic_handlers['nodes_will/+'](msg)
            return

        # Type 2: controller_tag/your_tag/action
        #         currently, action can be request/reply
        #         tag format: venderid_groupid_nodeid
        # dest_tag = topic_split[0]
        # source_tag = topic_split[1]
        action = topic_split[2]
        if action in self.action_handlers:
            logger.debug("start handle action")
            self.action_handlers[action](msg)

    def _on_action_request(self, msg):
        self._session_manager.handle_request(msg)

    def _on_action_reply(self, msg):
        self._session_manager.handle_reply(msg)

    def send_rpc_request(self, target_tag, method, params, listener=None):
        self._session_manager.send_rpc_request(target_tag, self._my_tag, method, params, listener)

    def topic_handler(self, topic):
        """ A decorator to register a function as topic handler
        :param topic:
        :return:
        """
        def decorator(f):
            self.topic_handlers[topic] = f
            return f
        return decorator

    def rpc_handler(self, method_name):
        """ A decorator to register a function as rpc handler
        :param method_name:
        :return:
        """
        def decorator(f):
            self._session_manager.register_rpc_handler(method_name, f)
            return f
        return decorator

    def forward_request_hook(self, method_name):
        """ A decorator to register a function as forward request hook
        :param method_name:
        :return:
        """
        def decorator(f):
            self._session_manager.register_forward_request_hook(method_name, f)
            return f
        return decorator

    def forward_reply_hook(self, method_name):
        """ A decorator to register a function as forward reply hook
        :param method_name:
        :return:
        """
        def decorator(f):
            self._session_manager.register_forward_reply_hook(method_name, f)
            return f
        return decorator

    def publish(self, topic, payload=None, qos=0, retain=False):
        self._ext_mqttc.pub(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0):
        self._ext_mqttc.sub(topic, qos)

    def signal(self, stag):
        self._session_manager.signal(stag)

    def run(self):
        self.action_handlers = {"request": self._on_action_request,
                                "reply": self._on_action_reply}

        self._ext_mqttc.on_connect = self._on_connect_wrapper
        self._ext_mqttc.on_message = self._on_message_wrapper

        try:
            self._ext_mqttc.will_set('nodes_will/' + self._my_tag, self._my_tag, 2, False)
            self._ext_mqttc.connect(self._broker_url, 1883, 60)
            self._ext_mqttc.sub(self._my_tag + "/+/request", qos=2)
            self._ext_mqttc.sub(self._my_tag + "/+/reply", qos=2)
            for topic in self.topic_handlers.keys():
                self._ext_mqttc.sub(topic, qos=2)

            self._ext_mqttc.loop_forever()
        except KeyboardInterrupt:
            self._ext_mqttc.disconnect()

