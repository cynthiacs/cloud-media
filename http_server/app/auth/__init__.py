from flask import Blueprint

from ..models import Vendor

auth = Blueprint('auth', __name__)

from . import views

"""
create default Vendor
"""
cur_vendor = Vendor.objects(vid="V0001").first()
if cur_vendor is None:
    cur_vendor = Vendor(vid="V0001", username="Leadcore", password="abcd.1234", role="administrator", active=True)
    cur_vendor.save()
