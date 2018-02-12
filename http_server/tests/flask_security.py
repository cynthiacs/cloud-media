
from flask import Flask, render_template
from flask_mongoengine import MongoEngine

from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_bootstrap import Bootstrap

# Create app
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

# Create database connection object
db = MongoEngine(app)
bootstrap = Bootstrap(app)

from main import main as main_blueprint
from auth import auth as auth_blueprint
app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    user_datastore.create_user(email='matt@nobien.net', password='password')


if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)
