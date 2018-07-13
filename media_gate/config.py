import os

_CM_MQTT_HOST = os.environ.get('CM_MQTT_HOST')
_CM_MONGO_HOST = os.environ.get('CM_MONGO_HOST')
_CM_FLASK_HOST = os.environ.get('CM_FLASK_HOST')
_user_admin_login_url = "http://%s:8085/login_mg" % (_CM_FLASK_HOST, )


config = {
    "mqtt":{
        "broker_url": _CM_MQTT_HOST,
        "broker_port":1883,
        "connect_timeout_s":60
    },
    "mongo":{
        "server_url":_CM_MONGO_HOST,
        "server_port":27017
    },
    "cloud_ali":{
        "live":{
        },
        "vod":{
        },
        "oss":{
        }
    },
    "user_admin":{
        "login_url":_user_admin_login_url
    },
    "media_gate":{
        "encrypt":False
    }
}
