"""

"""
import random
from flask import url_for, redirect, render_template, request, flash, json
from flask_login import login_required, current_user

from . import user
from ..models import User, CmGroup
from .. import messages


@user.route('/user/new', methods=['GET', 'POST'])
@login_required
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
        new_user.token = "token"
        if "active" in request.form and request.form["active"] == "on":
            new_user.active = True
        else:
            new_user.active = False
        new_user.role = request.form["role"]
        cur_group = CmGroup.objects.get_or_404(gid=request.form["group"])
        if cur_group.count is None:
            cur_group.count = 0
        cur_group_count = cur_group.count + 1
        cur_group.update(count=cur_group_count)
        new_user.group = cur_group
        new_user.vid = current_user.vid
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

    return render_template('user/new.html', groups=groups, account=account, vendor=current_user)


@user.route('/user/edit/<account>', methods=['GET', 'POST'])
@login_required
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
        old_group = cur_user.group
        new_group = CmGroup.objects.get_or_404(gid=request.form["group"])
        if cur_user.group is new_group:
            pass
        else:
            new_group_count = new_group.count + 1
            new_group.update(count=new_group_count)
            old_group_count = old_group.count - 1
            old_group.update(count=old_group_count)
            cur_user.group = new_group

        cur_user.vendor = request.form["vendor"]
        cur_user.update(username=cur_user.username, password=cur_user.password, active=cur_user.active,
                        role=cur_user.role, group=cur_user.group)
        return json.dumps({"result": "success"})
        # return "success"
        # return redirect(url_for('user.manage'))

    return render_template('user/edit.html', user=cur_user, groups=groups)


@user.route('/user/delete/<account>', methods=['GET', 'POST'])
@login_required
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
        cur_group = CmGroup.objects.get_or_404(gid=cur_user.group.gid)
        cur_group_count = cur_group.count - 1
        cur_group.update(count=cur_group_count)
        cur_user.delete()

    return "success"
    # return redirect(url_for('user.manage'))


@user.route('/user/manage', methods=['GET', 'POST'])
@login_required
def manage():
    """
    the user manager data from the db
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = User.objects.paginate(page=page, per_page=255)
    users = pagination.items
    pull_count = 0
    pusher_count = 0
    pull_online_count = 0
    pusher_online_count = 0
    for cur_user in users:
        if cur_user.role == 'puller':
            pull_count = pull_count + 1
            if cur_user.online > 0:
                pull_online_count = pull_online_count + 1
        else:
            pusher_count = pusher_count + 1
            if cur_user.online > 0:
                pusher_online_count = pusher_online_count + 1
    return render_template('user/manage.html', users=users, pull_count=pull_count,
                           pusher_count=pusher_count, total=pull_count + pusher_count,
                           pull_online_count=pull_online_count, pusher_online_count=pusher_online_count)


@user.route('/user/view/<account>', methods=['GET', 'POST'])
def view(account):
    print(account)
    return render_template('user/puller.html')
