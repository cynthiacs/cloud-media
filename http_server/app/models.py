from flask_login import login_manager, login_user
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from werkzeug.security import generate_password_hash

from . import db

"""
class Vendor(db.Document):
    vid = db.StringField(max_length=80)
    description = db.StringField(max_length=255)


class Group(db.Document):
    gid = db.StringField(max_length=80)
    description = db.StringField(max_length=255)

    @staticmethod
    def add_group(id, desc):
        pass
"""


class Permission:
    PULL = 0x01
    PUSH = 0x02


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


class CmVendor(db.Document):
    vid = db.StringField(max_length=64)
    username = db.StringField(max_length=64)

    def __repr__(self):
        return '<Group %r>' % self.username


class User(db.Document, UserMixin):
    account = db.StringField(max_length=64)
    username = db.StringField(max_length=64)
    password = db.StringField(max_length=16)
    token = db.StringField(max_length=64)
    # password_hash = db.StringField(max_length=128)
    active = db.BooleanField(default=True)
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

    def is_active(self):
        return self.active is True

    def group_selected(self, gid):
        return self.group.gid == gid

    def role_radio(self):
        return self.role == "Puller"

    def __repr__(self):
        return '<User %r>' % self.username
