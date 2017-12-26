"""
Extended MQTT module to provide a P2P message feature.
"""
import paho.mqtt.client as mqtt
import re
import logging
import sys
import json

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


class ExtSession(object):
    def __init__(self, context, mqtt_msg):
        self.context = context
        self._msg = mqtt_msg

        topic_split = mqtt_msg.topic.split('/')
        self._controller_id = topic_split[0]
        self._source_id = topic_split[1]

        payload = eval(mqtt_msg.payload)

        self._method_name = payload['method']
        self._method_params = payload['params']
        self._dest_id = self._method_params['target_id']
        self._method_id = payload['id']
        # self.session_tag = self._source_id + self._dest_id + self._method_id
        self.session_tag = self._dest_id + self._method_id

        self.iport_request_topic = "%s/%s/request" % (self._controller_id, self._source_id)
        self.iport_reply_topic = "%s/%s/reply" % (self._source_id, self._controller_id)
        self.oport_request_topic = "%s/%s/request" % (self._dest_id, self._controller_id)
        self.oport_reply_topic = "%s/%s/reply" % (self._controller_id, self._dest_id)
        pass

    @staticmethod
    def make_session_tag_from_oport_reply(self, mqtt_msg):
        topic_split = mqtt_msg.topic.split('/')
        _dest_id = topic_split[1]
        payload = eval(mqtt_msg.payload)
        return _dest_id + payload['id']

    def send_oport_request(self):
        topic = self.oport_request_topic
        payload = self._msg.payload
        logger.debug("send_oport_request \n\t %s \n\t %s" %
                     ("topic: " + topic, "payload: " + payload))
        self.context.ext_mqtt_client.publish(topic, payload, qos=2, retain=False)

    def send_iport_reply(self, result):
        topic = self.iport_reply_topic
        payload = '{"jsonrpc": "2.0", "result": "%s", "id": "%s"}' % (result, self._method_id)
        logger.debug("send_iport_reply \n\t %s \n\t %s" %
                     ("topic: " + topic, "payload: " + payload))
        self.context.ext_mqtt_client.publish(topic, payload, qos=2, retain=False)


class ExtSessionManager(object):
    def __init__(self, context):
        self.context = context
        self._ext_sessions = {}
        self._method_hook = {}

    def handle_iport_request(self, iport_request_msg):
        s = ExtSession(self.context, iport_request_msg)

        ret = True
        if s._method_name in self._method_hook:
            ret = self._method_hook[s._method_name](s._method_params)

        if ret:
            self._ext_sessions[s.session_tag] = s
            s.send_oport_request()
        else:
            s.send_iport_reply("ERROR: controller cannot handle this request.")

    def handle_oport_reply(self, oport_reply_msg):
        # to handle hooked listener ?

        session_tag = ExtSession.make_session_tag_from_oport_reply(oport_reply_msg)
        if session_tag in self._ext_sessions:
            self._ext_sessions[session_tag].send_iport_reply("OK")
        else:
            logger.error("@handle_oport_reply session not found!")

    def register_iport_method_hook(self, hook):
        """
        :param hook:
            @handle_iport_request ret = _method_hook[s._method_name](s._method_params)
        :return:
        """
        self._method_hook[hook.__name__] = hook

    def register_oport_reply_hook(self, id):
        pass

class P2PMqtt(object):
    """
    P2PMqtt supports request and response mode based on MQTT
    """
    def __init__(self, *, broker_url, whoami='controller'):
        self.context = ExtMqttContext()

        self._broker_url = broker_url
        self._whoami = whoami

        self._ext_mqttc = ExtMqtt(self)

        self.topic_handlers = {}
        self.action_handlers = {}

        # for action reqeust
        self._request_methods = {}
        self._jrpc_id = 0

        # for action reply
        self._reply_lisener = {}

        self.context.ext_mqtt_client = self._ext_mqttc

        # for ext reqeust/reply
        self._ext_session_manager = ExtSessionManager(self.context)

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
            self.topic_handlers[msg.topic](msg)
            return

        # Type 2: controller/your_id/action
        #         currently, action can be request/reply
        topic_split = msg.topic.split('/')
        whoami = topic_split[0]
        whoareyou = topic_split[1]
        action = topic_split[2]
        logger.debug("whoami:%s, whoareyou:%s, action:%s" % (whoami, whoareyou, action))

        if whoami != self._whoami:
            logger.error("this message is not for %s!!!" % self._whoami)
        elif action in self.action_handlers:
            self.action_handlers[action](msg)

    def _on_action_request(self, msg):
        topic_split = msg.topic.split('/')
        whoami = topic_split[0]
        whoareyou = topic_split[1]

        if msg.payload is None:
            logger.error("payload should not be None !")
            raise ValueError("request json error")

        rpc = eval(msg.payload)
        if 'method' not in rpc or 'params' not in rpc \
                or 'id' not in rpc:
            raise "reqeust's format is not correct"

        method = rpc['method']
        params = rpc['params']
        id = rpc['id']
        logger.debug("method:%s, params:%s, id:%s" % (method, params, id))

        ret = "OK"
        if method in self._request_methods:
            ret = self._request_methods[method](params)
            if ret is None:
                logger.error("handler should return something !")
        else:
            ret = 'ERROR: method %s is not supported'

        topic = whoareyou + "/" + whoami + "/reply"
        payload = '{"jsonrpc": "2.0", "result":"' \
                  + ret + '", "id":"' + str(id) + '"}'

        self.mqtt_publish(topic, payload, qos=2, retain=False)

    def _on_action_reply(self, msg):
        rpc = eval(msg.payload)
        if 'result' not in rpc or 'id' not in rpc:
            raise "reqeust's format is not correct"

        result = rpc['result']
        id = rpc['id']

        if id in self._reply_lisener:
            self._reply_lisener[id](result)
            del self._reply_lisener[id]
        else:
            logger.error("this id should not reply to me!")

    def _on_action_ext_request(self, msg):
        """
        topic: controller/id/ext_request
        payload:
        {
         jsonrpc: 2.0
         method: xxx
         params: xxx
              targetid: xxx
         id: xxx
         }
        """
        self._ext_session_manager.handle_iport_request(msg)

    def _on_action_ext_reply(self, msg):
        """
        topic: controller/id/ext_reply
        payload:
        {
         jsonrpc: 2.0
         result: xxx
         id: xxx
         }
         """
        self._ext_session_manager.handle_oport_reply(msg)

    def register_topic_handler(self, topic, handler, qos=2):
        self.mqtt_subscribe(topic, qos)
        if not callable(handler):
            raise "params error"
        self.topic_handlers[topic] = handler

    def register_request_method(self, name, method):
        """
        :param method: the signature should be
            str foo(mqtt_msg)
        :return:
        """
        if not callable(method):
            raise "you must register a function!"
        self._request_methods[name] = method

    def register_reply_lisener(self, id, lisener):
        self._reply_lisener[id] = lisener

    def register_ext_method_hook(self, hook):
        self._ext_session_manager.register_iport_method_hook(hook)

    def send_request(self, target_node_id, method, params, listener=None):
        """
        send json rpc request to target node
        :param target_node_id:
        :param method:
        :param params:
        :param listener:
        :return:
        """
        topic = target_node_id + "/" + self._whoami + "/request"

        if params[0] == "{":
            payload = '{"jsonrpc": "2.0", "method":"' + method + '"' \
                ',"params":' + params + ',"id":"' + str(self._jrpc_id) + '"}'
        else:
            payload = '{"jsonrpc": "2.0", "method":"' + method + '"' \
                ',"params":"' + params + '"' \
                ',"id":"' + str(self._jrpc_id) + '"}'

        if listener is not None:
            self.register_reply_lisener(str(self._jrpc_id), listener)

        self._jrpc_id += 1

        logger.debug("<== publish")
        logger.debug("\t topic:" + topic)
        logger.debug("\t payload:" + payload)
        self._ext_mqttc.publish(topic, payload, qos=2, retain=False)

    def mqtt_publish(self, topic, payload=None, qos=0, retain=False):
        logger.debug("<== publish")
        logger.debug("\t topic:" + topic)
        logger.debug("\t payload:" + payload)
        logger.debug("\t qos:" + str(qos))
        logger.debug("\t retain:" + str(retain))
        self._ext_mqttc.publish(topic, payload, qos, retain)

    def mqtt_subscribe(self, topic, qos=0):
        self._ext_mqttc.subscribe(topic, qos)

    def loop(self):
        self.action_handlers = {"request": self._on_action_request,
                                "reply": self._on_action_reply,
                                "ext_request": self._on_action_ext_request,
                                "ext_reply": self._on_action_ext_reply}

        self._ext_mqttc.on_connect = self._on_connect_wrapper
        self._ext_mqttc.on_message = self._on_message_wrapper

        try:
            self._ext_mqttc.will_set('nodes_will/' + self._whoami, self._whoami, 2, False)
            self._ext_mqttc.connect(self._broker_url, 1883, 60)
            self._ext_mqttc.subscribe(self._whoami + "/+/request", qos=2)
            self._ext_mqttc.subscribe(self._whoami + "/+/reply", qos=2)
            for topic in self.topic_handlers.keys():
                self._ext_mqttc.subscribe(topic, qos=2)

            self._ext_mqttc.loop_forever()
        except KeyboardInterrupt:
            self._ext_mqttc.disconnect()

