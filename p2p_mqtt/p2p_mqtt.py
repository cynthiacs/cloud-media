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


def enable_p2p_mqtt_logger(level=logging.DEBUG):
    logger.setLevel(level)
    format = logging.Formatter("%(asctime)s - %(message)s")
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(format)
    logger.addHandler(sh)


class ExtMqtt(mqtt.Client):
    """
    ExtMqtt extends MqttClient to support p2p feature
    """
    def __init__(self, whoami="controller"):
        # handlers signature : handler(jrpc)
        self.request_handlers = {}
        self.reply_handlers = {}
        self.topic_handlers = {}
        self._whoami = whoami

        """ the default parameters:
            client_id = "", clean_session = True, userdata = None,
            protocol = MQTTv311, transport = "tcp" 
        """
        super().__init__()

    @property
    def whoami(self):
        return self._whoami


class P2PMqtt(object):
    """
    P2PMqtt supports request and response mode based on MQTT
    """
    def __init__(self, *, broker_url, whoami='controller'):
        self._broker_url = broker_url
        self._whoami = whoami
        self._jrpc_id = 0
        self._ext_mqttc = ExtMqtt(whoami)

    def register_request_handler(self, method, handler):
        """
        register request handler

        :param method: the json rpc method
        :param handler: what the method to trigger in this node
        :return: string to send back throght jrpc
        """
        if method is None or handler is None:
            raise ValueError("parameter error for register_request_handler")
        if self._ext_mqttc is not None:
            logger.debug("p2p.mqtt register_request_handler")
            self._ext_mqttc.request_handlers[method] = handler
        else:
            raise ValueError("p2p_mqtt calling sequence error for"
                             " register_request_handler ")

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

        if True:
            payload = '{"jsonrpc": "2.0", "method":"' + method + '"' \
                ',"params":"' + params + '"' \
                ',"id":"' + str(self._jrpc_id) + '"}'
        else:
            payload = '{"jsonrpc": "2.0", "method":"' + method + '"' \
                ',"params":' + params + ',"id":"' + str(self._jrpc_id) + '"}'

        if listener is not None:
            self._install_reply_listener(str(self._jrpc_id), listener)
        self._jrpc_id += 1

        logger.debug("<== publish")
        logger.debug("\t topic:" + topic)
        logger.debug("\t payload:" + payload)
        self._ext_mqttc.publish(topic, payload, qos=2, retain=False)

    def register_topic_handler(self, topic, handler, qos=2):
        self.mqtt_subscribe(topic, qos)

        if self._ext_mqttc is not None:
            logger.debug("p2p.mqtt register_request_handler")
            self._ext_mqttc.topic_handlers[topic] = handler
        else:
            raise ValueError("p2p_mqtt calling sequence error for"
                             " register_request_handler ")

    def mqtt_publish(self, topic, payload=None, qos=0, retain=False):
        logger.debug("<== publish")
        logger.debug("\t topic:" + topic)
        logger.debug("\t payload:" + payload)
        self._ext_mqttc.publish(topic, payload, qos, retain)

    def mqtt_subscribe(self, topic, qos=0):
        self._ext_mqttc.subscribe(topic, qos)

    def _install_reply_listener(self, id, listener):
        """ register reply handler

        :param id: is the json rpc's reply id.
        :param listener: is the function to check the json rpc's result.
        expected handler's signature is:
            handler(result)
        """
        if id is None or listener is None:
            raise ValueError("parameter error")
        if self._ext_mqttc is not None:
            self._ext_mqttc.reply_handlers[id] = listener
        else:
            raise ValueError("should not be here")

    @staticmethod
    def _on_connect(ext_mqttc, obj, flags, rc):
        logger.info("on_connect with rc: " + str(rc))

    @staticmethod
    def _on_message(ext_mqttc, obj, msg):
        logger.debug("==> _on_message")
        logger.debug("\t topic: " + msg.topic)
        logger.debug("\t qos: " + str(msg.qos))
        logger.debug("\t payload" + str(msg.payload))

        if re.match(ext_mqttc.whoami + "/\S*/request", msg.topic) is not None:
            if msg.payload is None:
                logger.error("payload should not be None !")
                raise ValueError("request json error")
            jrpc = json.loads(msg.payload)
            if jrpc is None:
                raise ValueError("request json error")
            if jrpc["method"] is None:
                raise ValueError("jrpc format error")
            method = jrpc["method"]
            params = str(jrpc["params"])
            logger.debug("request method: " + method)
            logger.debug("request params: " + params)
            if method in ext_mqttc.request_handlers:
                ret = ext_mqttc.request_handlers[method](jrpc)
                if ret is None:
                    logger.error("handler should return something !")
                    ret = "OK"

                whoareyou = msg.topic.split("/")[1]
                topic = whoareyou + "/" + ext_mqttc.whoami + "/reply"
                payload = '{"jsonrpc": "2.0", "result":"' \
                    + ret + '", "id":"' + str(jrpc["id"]) + '"}'

                logger.debug("<== publish")
                logger.debug("\t topic: " + topic)
                logger.debug("\t qos: " + str(2))
                logger.debug("\t payload" + str(payload))
                ext_mqttc.publish(topic, payload, qos=2, retain=False)

        elif re.match(ext_mqttc.whoami + "/\S*/reply", msg.topic) is not None:
            jrpc = json.loads(msg.payload)
            if jrpc is None:
                raise ValueError("request json error")
            if jrpc["result"] is None:
                raise ValueError("jrpc format is error")
            json_id = str(jrpc["id"])
            result = jrpc["result"]
            if json_id in ext_mqttc.reply_handlers:
                ext_mqttc.reply_handlers[json_id](result)
                logger.info("delete reply lisener, NOTE, this is not same as request handler....")
                del ext_mqttc.reply_handlers[json_id]
        else:
            if ext_mqttc.topic_handlers is not None:
                if msg.topic in ext_mqttc.topic_handlers:
                    ext_mqttc.topic_handlers[msg.topic](msg)

            logger.info("un-handed topic:" + msg.topic)

    def loop(self):
        self._ext_mqttc.on_connect = self._on_connect
        self._ext_mqttc.on_message = self._on_message

        try:
            self._ext_mqttc.will_set('nodes_will/' + self._whoami, self._whoami, 2, False)
            self._ext_mqttc.connect(self._broker_url, 1883, 60)
            self._ext_mqttc.subscribe(self._whoami + "/+/request", qos=2)
            self._ext_mqttc.subscribe(self._whoami + "/+/reply", qos=2)
            self._ext_mqttc.loop_forever()
        except KeyboardInterrupt:
            self._ext_mqttc.disconnect()


""" ==================================================
following is test code 
======================================================"""
def _test_hello_handler(params):
    print("hello_handler")
    print("params:" + params)
    return "OK"


def _test_hello_listener(result):
    print("hello_listener")
    print("result: " + result)


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='alex')
    p2pc.register_request_handler("hello", _test_hello_handler)
    p2pc.send_request("controller", "hello", "hhhhhh", _test_hello_listener)
    p2pc.loop()
