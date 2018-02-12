from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from flask_bootstrap import WebCDN, ConditionalCDN, BOOTSTRAP_VERSION, JQUERY_VERSION, HTML5SHIV_VERSION, RESPONDJS_VERSION

bootstrap = Bootstrap()
db = MongoEngine()
moment = Moment()

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


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    #app.config['SECRET_KEY'] = 'super-secret'
    app.config['SECRET_KEY'] = 'plaintext'

    ##### yxd 
    app.config['SECURITY_PASSWORD_HASH'] = 'plaintext'
    app.config['SECURITY_PASSWORD_SALT'] = None
    app.config['SECURITY_PASSWORD_SINGLE_HASH'] = True
    app.config['SECURITY_PASSWORD_SCHEMES'] = 'plaintext'

    # MongoDB Config
    app.config['MONGODB_DB'] = 'mydatabase'
    app.config['MONGODB_HOST'] = 'localhost'
    app.config['MONGODB_PORT'] = 27017

    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    #change_cdn_domestic(app)

    from app.main import main as main_blueprint
    from app.auth import auth as auth_blueprint
    from app.apis import apis as apis_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(apis_blueprint)

    return app

