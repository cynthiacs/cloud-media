from flask import Blueprint

__all__ = []
__version__ = '0.0.1'
__author__ = 'Wang'

group = Blueprint('group', __name__)

from . import views
