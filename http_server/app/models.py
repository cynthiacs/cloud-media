from flask_login import login_manager, login_user
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required

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


class User(db.Document, UserMixin):
    account = db.StringField(max_length=64)
    username = db.StringField(max_length=64)
    password = db.StringField(max_length=16)
    active = db.BooleanField(default=True)
    role = db.StringField(max_length=80)
    group = db.StringField(max_length=80)
    vendor = db.StringField(max_length=80)

    # roles = db.ListField(db.ReferenceField(Role), default=[])
    # groups = db.ListField(db.ReferenceField(Group), default=[])
    # confirmed_at = db.DateTimeField()

    def verify_password(self, pwd):
        return self.password == pwd

    def __repr__(self):
        return '<User %r>' % self.username


class CmGroup(db.Document):
    gid = db.StringField(max_length=64)
    username = db.StringField(max_length=64)

    def __repr__(self):
        return '<Group %r>' % self.username
