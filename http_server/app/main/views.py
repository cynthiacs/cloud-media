from flask import render_template, session, redirect, url_for
from flask_security import Security, MongoEngineUserDatastore, \
     UserMixin, RoleMixin, login_required

from . import main
from .forms import NewUserForm
from ..models import User

@main.route('/yxd')
@login_required
def home():
    return render_template('index.html')


@main.route('/new_user')
def new_user():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User()
        user.uid = form.uid.data
        user.account = form.account.data
        user.password = form.account.password
        user.email = form.email.data
        user.active = form.active.data
        user.role = form.role.data    # or fetch from Role collection?
        user.group = form.group.data
        user.confirmed_at = form.confirmed_at.data
        user.save()
        return "OK"
        #return redirect(url_for('.user', username=user.username))
    return render_template('new_user.html', form=form)
