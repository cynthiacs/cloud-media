import os

_CM_MQTT_HOST = os.environ.get('CM_MQTT_HOST')
_CM_MONGO_HOST = os.environ.get('CM_MONGO_HOST')
_CM_FLASK_HOST = os.environ.get('CM_FLASK_HOST')
_cloud_ali_auth_url = "http://%s:8085/cm_add_live_detect_notify" % (_CM_FLASK_HOST, )

config = {
    "mqtt":{
        "broker_url":_CM_MQTT_HOST,
        "broker_port":1883,
        "connect_timeout_s":60
    },
    "mongo":{
        "server_url":_CM_MONGO_HOST,
        "server_port":27017
    },
    "cloud_ali":{
        "live":{
            "auth_url":_cloud_ali_auth_url,
            "auth_key":"yangxudong"
        },
        "vod":{
        },
        "oss":{
        }
    }
}
