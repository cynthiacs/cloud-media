from flask import Blueprint

from http_server.app.models import User

auth = Blueprint('auth', __name__)

from . import views

"""
create default Vendor
"""
cur_user = User.objects(account="V0001").first()
if cur_user is None:
    new_user = User()
    new_user.account = "V0001"
    new_user.username = "Vendor"
    new_user.password = "abcd.1234"
    new_user.role = "administrator"
    new_user.active = True
    new_user.save()
