"""

"""
import random
from flask import url_for, redirect, render_template, request, flash
from . import user
from ..models import User, CmGroup
from .. import messages


@user.route('/user/new', methods=['GET', 'POST'])
def new():
    """
    new one user
    :return:
    """

    if request.method == "POST":
        new_user = User()
        new_user.account = request.form["account"]
        new_user.username = request.form["username"]
        new_user.password = request.form["password"]
        if "active" in request.form and request.form["active"] == "on":
            new_user.active = True
        else:
            new_user.active = False
        new_user.role = request.form["role"]
        # new_user.group = request.form["group"]
        new_user.group = CmGroup.objects.get_or_404(gid=request.form["group"])
        new_user.vendor = request.form["vendor"]
        new_user.save()
        return redirect(url_for('user.manage'))

    groups = CmGroup.objects()
    while True:
        randomnum = random.randint(100000, 999999)
        account = "A" + str(randomnum)
        user = User.objects(account=account).first()
        if user is None:
            break

    return render_template('user/new.html', groups=groups, account=account, vendor="Vendor")


@user.route('/user/edit/<account>', methods=['GET', 'POST'])
def edit(account):
    """
    edit the account of the user
    :param account:
    :return:
    """
    groups = CmGroup.objects()
    cur_user = User.objects.get_or_404(account=account)
    if request.method == "POST":
        cur_user.username = request.form["username"]
        cur_user.password = request.form["password"]
        if "active" in request.form and request.form["active"] == "on":
            cur_user.active = True
        else:
            cur_user.active = False
        cur_user.role = request.form["role"]
        # new_user.group = request.form["group"]
        cur_user.group = CmGroup.objects.get_or_404(gid=request.form["group"])
        cur_user.vendor = request.form["vendor"]
        cur_user.update(username=cur_user.username, password=cur_user.password, active=cur_user.active,
                        role=cur_user.role, group=cur_user.group)
        return redirect(url_for('user.manage'))

    return render_template('user/edit.html', user=cur_user, groups=groups)


@user.route('/user/delete/<account>', methods=['GET', 'POST'])
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
    return render_template('user/manage.html', users=users)
