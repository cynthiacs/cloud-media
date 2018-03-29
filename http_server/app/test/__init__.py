from flask import Blueprint

bp_test = Blueprint('bp_test', __name__)

from . import views
