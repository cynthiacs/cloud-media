from flask import render_template, session, redirect, url_for
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required

from . import main
from .forms import NewUserForm
from ..models import User


@main.route('/yxd')
@login_required
def home():
    return render_template('auth/login.html')


@main.route('/about')
def about():
    return render_template('about/about_us.html')
