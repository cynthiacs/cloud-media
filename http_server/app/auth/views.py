from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(account=form.account.data).first()
        if user is not None and user.verify_password(form.password.data):
            return "OK"
        else:
            return "ERROR"

        #flash('Not Implement Yet!')
    return render_template('auth/login.html', form=form)


