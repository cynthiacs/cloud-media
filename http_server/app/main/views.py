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


"""
@main.route('/new_user', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()
    print("new_user+++")
    if form.validate_on_submit():
        user = User()
        user.uid = form.uid.data
        user.account = form.account.data
        user.username = form.username.data
        print(user.account)
        user.active = form.active.data
        user.role = form.role.data  # or fetch from Role collection?
        user.group = form.group.data
        print(user.role)
        print(user.group)
        user.password = form.password.data
        print(user.password)
        user.save()
        return redirect(url_for('main.get_user', account=user.account))
        # return redirect(url_for('.user', username=user.username))
    return render_template('new_user.html', form=form)


@main.route('/get_user/<account>', methods=['GET', 'POST'])
def get_user(account):
    print('get_user+++')
    user = User.objects(account=account).first()
    print(user.role)
    print(user.group)
    user.delete()
    return render_template('404.html')
"""
