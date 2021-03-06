from flask import current_app
from flask_login import login_manager, login_user
from flask_login._compat import unicode
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from werkzeug.security import generate_password_hash

from . import db


class Permission:
    PULL = 0x01
    PUSH = 0x02
    ADMINISTRATOR = 0xFF


class Role(db.Document, RoleMixin):
    rid = db.StringField(max_length=80)
    name = db.StringField(max_length=80, unique=True)
    permission = db.IntField()
    description = db.StringField(max_length=255)


class CmGroup(db.Document):
    gid = db.StringField(max_length=64)
    name = db.StringField(max_length=64)
    count = db.IntField()

    def is_default(self):
        return self.gid == "G00000"

    def __repr__(self):
        return '<Group %r>' % self.username


class Vendor(db.Document, UserMixin):
    vid = db.StringField(max_length=64)
    username = db.StringField(max_length=64)
    password = db.StringField(max_length=16)
    active = db.BooleanField(default=True)
    role = db.StringField(default="administrator")

    def verify_password(self, pwd):
        return self.password == pwd

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active is True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<Vendor %r>' % self.username


class User(db.Document, UserMixin):
    account = db.StringField(max_length=64)
    username = db.StringField(max_length=64)
    password = db.StringField(max_length=16)
    token = db.StringField(max_length=64)
    # password_hash = db.StringField(max_length=128)
    active = db.BooleanField(default=True)
    online = db.IntField(default=0)
    role = db.StringField(max_length=80)
    # group = db.StringField(max_length=80)
    group = db.ReferenceField(CmGroup)
    vid = db.StringField(max_length=16)
    vendor = db.StringField(max_length=80)

    # roles = db.ListField(db.ReferenceField(Role), default=[])
    # groups = db.ListField(db.ReferenceField(Group), default=[])
    # confirmed_at = db.DateTimeField()

    """
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    """

    def verify_password(self, pwd):
        return self.password == pwd

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active is True

    def is_online(self):
        return self.online > 0

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def group_selected(self, gid):
        return self.group.gid == gid

    def role_radio(self):
        return self.role == "puller"

    def __repr__(self):
        return '<User %r>' % self.username
