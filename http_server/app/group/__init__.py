from flask import Blueprint

__all__ = []
__version__ = '0.0.1'
__author__ = 'Wang'

group = Blueprint('group', __name__)

from . import views
from ..models import CmGroup

"""
create default group
"""
cur_group = CmGroup.objects(gid="G00000").first()
if cur_group is None:
    new_group = CmGroup()
    new_group.gid = "G00000"
    new_group.name = "Default Group"
    new_group.count = 0
    new_group.save()
