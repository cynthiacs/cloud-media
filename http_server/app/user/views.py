"""

"""
from flask import url_for, redirect, render_template, request, flash

from . import user
from .forms import NewUserForm, EditUserForm
from ..models import User, CmGroup
from .. import messages


@user.route('/user/new', methods=['GET', 'POST'])
def new():
    """
    new one user
    :return:
    """
    groups = CmGroup.objects()
    form = NewUserForm(groups=groups)
    print(groups)
    if form.validate_on_submit():
        new_user = User()
        new_user.account = form.account.data
        new_user.username = form.username.data
        new_user.password = form.password.data
        new_user.active = form.active.data
        new_user.role = form.role.data
        new_user.group = form.group.data
        new_user.vendor = form.vendor.data
        new_user.save()
        return redirect(url_for('user.manage'))
    return render_template('user/new.html', form=form)


@user.route('/user/edit/<account>', methods=['GET', 'POST'])
def edit(account):
    """
    edit the account of the user
    :param account:
    :return:
    """
    groups = CmGroup.objects()
    cur_user = User.objects.get_or_404(account=account)
    form = EditUserForm(user=cur_user, groups=groups)
    if form.validate_on_submit():
        # cur_user.account = form.account.data
        cur_user.username = form.username.data
        cur_user.password = form.password.data
        cur_user.active = form.active.data
        cur_user.role = form.role.data
        cur_user.group = form.group.data
        cur_user.vendor = form.vendor.data
        cur_user.update(username=cur_user.username, password=cur_user.password, active=cur_user.active,
                        role=cur_user.role, group=cur_user.group)
        return redirect(url_for('user.manage'))
    form.account.data = cur_user.account
    form.username.data = cur_user.username
    form.password.data = cur_user.password
    form.active.data = cur_user.active
    form.role.data = cur_user.role
    form.group.data = cur_user.group
    form.vendor.data = cur_user.vendor

    return render_template('user/edit.html', form=form, user=user)


@user.route('/user/delete/<account>')
def delete(account):
    """
    delete the account of the user
    :param account:
    :return:
    """
    cur_user = User.objects(account=account).first()
    if cur_user is None:
        flash(messages.user_not_found)
    else:
        cur_user.delete()
    return redirect(url_for('user.manage'))


@user.route('/user/manage')
def manage():
    """
    the user manager data from the db
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = User.objects.paginate(page=page, per_page=255)
    users = pagination.items
    print(users)
    return render_template('user/manage.html', users=users)
