import os


config = {
    "mqtt": {
        "broker_url":os.environ.get('CM_MQTT_HOST'),
        "broker_port": 1883,
        "connect_timeout_s": 60
    },
    "mongo": {
        "server_url":os.environ.get('CM_MONGO_HOST'),
        "server_port": 27017,
        "db_name": "usermanager"
    },
    "flask_app": {
        "host": "0.0.0.0",
        "port": 8085
    },
}
