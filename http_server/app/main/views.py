from flask import render_template, session, redirect, url_for
from flask_security import Security, MongoEngineUserDatastore, \
     UserMixin, RoleMixin, login_required

from . import main

@main.route('/yxd')
@login_required
def home():
    return render_template('index.html')

