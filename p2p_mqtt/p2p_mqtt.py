"""
Extended MQTT module to provide a P2P message feature.
"""
import paho.mqtt.client as mqtt
import logging


__all__ = ('P2PMqtt',)
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
                     ("topic: " + topic,
                      "payload: " + payload,
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
        self._payload = payload
        self._method_name = payload['method']
        self._method_params = payload['params']
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


class RpcSession(Session):
    def __init__(self, context, mqtt_msg, reply_listener=None):
        Session.__init__(self, context, mqtt_msg)
        self._listener = reply_listener

        topic_split = self._msg.topic.split('/')
        self._dest_id = topic_split[0]
        self._source_id = topic_split[1]
        self.session_tag = self._dest_id + self._method_id
        self.request_topic = "%s/%s/request" % (self._dest_id, self._source_id)
        self.reply_topic = "%s/%s/reply" % (self._source_id, self._dest_id)

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
        self._controller_id = topic_split[0]
        self._source_id = topic_split[1]
        self._dest_id = self._method_params['target_id']

        # self.session_tag = self._source_id + self._dest_id + self._method_id
        self.session_tag = self._dest_id + self._method_id
        self.iport_request_topic = "%s/%s/request" % (self._controller_id, self._source_id)
        self.iport_reply_topic = "%s/%s/reply" % (self._source_id, self._controller_id)
        self.oport_request_topic = "%s/%s/request" % (self._dest_id, self._controller_id)
        self.oport_reply_topic = "%s/%s/reply" % (self._controller_id, self._dest_id)

    def send_request(self):
        topic = self.oport_request_topic
        payload = self._msg.payload
        self.send(topic, payload)

    def send_reply(self, result):
        topic = self.iport_reply_topic
        payload = '{"jsonrpc": "2.0", "result": "%s", "id": "%s"}' % (result, self._method_id)
        self.send(topic, payload)


class SessionManager(object):
    def __init__(self, context):
        self.context = context
        self._rpc_sessions = {}
        self._rpc_handler = {}

        self._forward_sessions = {}
        self._forward_request_hook = {}
        self._forward_reply_hook = {}
        self._jrpc_id = 0

    def send_rpc_request(self, target_tag, source_tag, method, params, listener):
        msg = mqtt.MQTTMessage()
        topic = target_tag + "/" + source_tag + "/request"
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
        ret = ""
        if s._method_name in self._rpc_handler:
            logger.debug("_rpc_handler: %s " %
                         self._rpc_handler[s._method_name].__name__)
            ret = self._rpc_handler[s._method_name](s._method_params)
            s.send_reply(ret)
            return

        logger.debug("_forward_handler")
        s = ForwardSession(self.context, iport_request_msg)

        if s._method_name in self._forward_request_hook:
            ret = self._forward_request_hook[s._method_name](s._method_params)
            if ret:
                self._forward_sessions[s.session_tag] = s
                s.send_request()
            else:
                s.send_reply("ERROR: method %s failed in controller hook" % s._method_name)
        else:
            logger.info("can not handle method: %s" % s._method_name)
            s.send_reply("ERROR: unknown method")

    def handle_reply(self, reply_msg):
        logger.debug("handle_reply")
        session_tag = Session.make_session_tag_from_reply(reply_msg)
        if session_tag in self._rpc_sessions:
            s = self._rpc_sessions[session_tag]
            s.call_listener(reply_msg)
        elif session_tag in self._forward_sessions:
            s = self._forward_sessions[session_tag]
            # reply hook has not implemented yet
            if s._method_name in self._forward_reply_hook:
                rpc = eval(reply_msg)
                if 'result' not in rpc or 'id' not in rpc:
                    raise "reqeust's format is not correct"
                self._forward_reply_hook[s._method_name](reply_msg)

            self._forward_sessions[session_tag].send_reply("OK")
            del self._forward_sessions[session_tag]
            logger.debug("@handle_oport_reply session:%s is deleted" % session_tag)
        else:
            logger.error("@handle_oport_reply session not found!")

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
    def __init__(self, *, broker_url, whoami='controller'):
        self._broker_url = broker_url
        self._whoami = whoami

        self._ext_mqttc = ExtMqtt(self)

        self.topic_handlers = {}
        self.action_handlers = {}

        self.context = ExtMqttContext()
        self.context.ext_mqtt_client = self._ext_mqttc

        self._session_manager = SessionManager(self.context)

    @staticmethod
    def _on_connect_wrapper(ext_mqttc, obj, flags, rc):
        logger.info("on_connect with rc: " + str(rc))

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


        # Type 2: controller_tag/your_tag/action
        #         currently, action can be request/reply
        #         tag format: venderid_groupid_nodeid
        topic_split = msg.topic.split('/')
        whoami = topic_split[0]
        whoareyou = topic_split[1]
        action = topic_split[2]
        logger.debug("whoami:%s, whoareyou:%s, action:%s" % (whoami, whoareyou, action))

        if action in self.action_handlers:
            logger.debug("start handle action")
            self.action_handlers[action](msg)

    def _on_action_request(self, msg):
        self._session_manager.handle_request(msg)

    def _on_action_reply(self, msg):
        self._session_manager.handle_reply(msg)

    def register_topic_handler(self, topic, handler, qos=2):
        # self.mqtt_subscribe(topic, qos)
        if not callable(handler):
            raise "params error"
        self.topic_handlers[topic] = handler

    def send_rpc_request(self, target_tag, method, params, listener=None):
        self._session_manager.send_rpc_request(target_tag, self._whoami, method, params, listener)

    def register_rpc_handler(self, method_name, handler):
        if not callable(handler):
            raise "you must register a function as handler!"
        self._session_manager.register_rpc_handler(method_name, handler)

    def register_forward_request_hook(self, method_name, hook):
        if not callable(hook):
            raise "you must register a function as hook!"
        self._session_manager.register_forward_request_hook(method_name, hook)

    def register_forward_reply_hook(self, method_name, hook):
        if not callable(hook):
            raise "you must register a function as hook!"
        self._session_manager.register_forward_reply_hook(method_name, hook)

    def mqtt_publish(self, topic, payload=None, qos=0, retain=False):
        self._ext_mqttc.pub(topic, payload, qos, retain)

    def mqtt_subscribe(self, topic, qos=0):
        self._ext_mqttc.sub(topic, qos)

    def loop(self):
        self.action_handlers = {"request": self._on_action_request,
                                "reply": self._on_action_reply}

        self._ext_mqttc.on_connect = self._on_connect_wrapper
        self._ext_mqttc.on_message = self._on_message_wrapper

        try:
            self._ext_mqttc.will_set('nodes_will/' + self._whoami, self._whoami, 2, False)
            self._ext_mqttc.connect(self._broker_url, 1883, 60)
            self._ext_mqttc.sub(self._whoami + "/+/request", qos=2)
            self._ext_mqttc.sub(self._whoami + "/+/reply", qos=2)
            for topic in self.topic_handlers.keys():
                self._ext_mqttc.sub(topic, qos=2)

            self._ext_mqttc.loop_forever()
        except KeyboardInterrupt:
            self._ext_mqttc.disconnect()

