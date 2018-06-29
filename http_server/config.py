import os

config = {
    "mqtt": {
        "broker_url": '47.100.125.222',
        "broker_port": 1883,
        "connect_timeout_s": 60
    },
    "mongo": {
        "server_url": '47.100.125.222',
        "server_port": 27017,
        "db_name": "usermanager"
    },
    "flask_app": {
        "host": "0.0.0.0",
        "port": 8085
    },
}
