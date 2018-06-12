from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_bootstrap import WebCDN, ConditionalCDN, BOOTSTRAP_VERSION, JQUERY_VERSION, HTML5SHIV_VERSION, \
    RESPONDJS_VERSION
from flask_mqtt import Mqtt
from config import config

db = MongoEngine()
mqtt = Mqtt()
"""
[TBD]
request: Check the terminal is online
solution: Application of flaskIO with MQTT
"""


def create_app():
    app = Flask(__name__)
    flask_config(app)

    init_db(app)
    int_bootstrap(app)
    init_flask_mqtt(app)
    init_login_manager(app)

    register_blueprint(app)

    return app


def flask_config(app):
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'plaintext'
    app.config['SECURITY_PASSWORD_HASH'] = 'plaintext'
    app.config['SECURITY_PASSWORD_SALT'] = None
    app.config['SECURITY_PASSWORD_SINGLE_HASH'] = True
    app.config['SECURITY_PASSWORD_SCHEMES'] = 'plaintext'


def init_db(app):
    app.config['MONGODB_DB'] = config['mongo']['db_name']
    app.config['MONGODB_HOST'] = config['mongo']['server_url']
    app.config['MONGODB_PORT'] = config['mongo']['server_port']
    db.init_app(app)


def int_bootstrap(app):
    bootstrap = Bootstrap()
    bootstrap.init_app(app)


def init_flask_mqtt(app):
    app.config['MQTT_BROKER_URL'] = config['mqtt']['broker_url']
    app.config['MQTT_BROKER_PORT'] = config['mqtt']['broker_port']
    mqtt.init_app(app)


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        :param user_id:  Object ID
        :return:
        """
        from .models import Vendor
        return Vendor.objects(id=user_id).first()


def register_blueprint(app):
    from app.main import main as main_blueprint
    from app.auth import auth as auth_blueprint
    from app.apis import apis as apis_blueprint
    from app.user import user as user_blueprint
    from app.group import group as group_blueprint
    from app.test import bp_test as bp_test_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(apis_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(group_blueprint)
    app.register_blueprint(bp_test_blueprint)


def change_cdn_domestic(tar_app):
    static = tar_app.extensions['bootstrap']['cdns']['static']
    local = tar_app.extensions['bootstrap']['cdns']['local']

    def change_one(tar_lib, tar_ver, fallback):
        tar_js = ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', fallback,
                                WebCDN('//cdn.bootcss.com/' + tar_lib + '/' + tar_ver + '/'))
        tar_app.extensions['bootstrap']['cdns'][tar_lib] = tar_js

    libs = {'jquery': {'ver': JQUERY_VERSION, 'fallback': local},
            'bootstrap': {'ver': BOOTSTRAP_VERSION, 'fallback': local},
            'html5shiv': {'ver': HTML5SHIV_VERSION, 'fallback': static},
            'respond.js': {'ver': RESPONDJS_VERSION, 'fallback': static}}

    for lib, par in libs.items():
        change_one(lib, par['ver'], par['fallback'])
