"""

"""
import random
from flask import url_for, redirect, render_template, request, flash
from flask_login import login_required

from .. import messages
from . import group
from ..models import CmGroup, User


@group.route('/group/new', methods=['GET', 'POST'])
@login_required
def new():
    """
    new one group
    :return:
    """
    if request.method == "POST":
        new_group = CmGroup()
        new_group.gid = request.form["gid"]
        new_group.name = request.form["name"]
        new_group.count = 0
        new_group.save()
        return redirect(url_for('group.manage'))

    while True:
        randomnum = random.randint(10000, 99999)
        gid = "G" + str(randomnum)
        cur_group = CmGroup.objects(gid=gid).first()
        if cur_group is None:
            break

    return render_template('group/new.html', gid=gid)


@group.route('/group/edit/<gid>', methods=['GET', 'POST'])
@login_required
def edit(gid):
    """
    edit the name gid of group
    :param gid:
    :return:
    """
    cur_group = CmGroup.objects.get_or_404(gid=gid)
    if request.method == "POST":
        cur_group.name = request.form["name"]
        cur_group.update(name=cur_group.name)
        return redirect(url_for('group.manage'))

    return render_template('group/edit.html', group=cur_group)


@group.route('/group/delete/<gid>', methods=['GET', 'POST'])
@login_required
def delete(gid):
    """
    delete the name gid of group
    :param gid:
    :return:
    """
    cur_group = CmGroup.objects(gid=gid).first()
    if cur_group is None:
        flash(messages.group_not_found)
    else:
        cur_group.delete()
    return "success"
    # return redirect(url_for('group.manage'))


@group.route('/group/manage')
@login_required
def manage():
    """
    group manage table data from db
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = CmGroup.objects.paginate(page=page, per_page=255)
    groups = pagination.items
    return render_template('group/manage.html', groups=groups)


@group.route('/group/details/<gid>')
@login_required
def details(gid):
    """
    group manage table data from db
    :return:
    """
    page = request.args.get('page', 1, type=int)
    cur_group = CmGroup.objects.get_or_404(gid=gid)
    pagination = User.objects(group=cur_group).paginate(page=page, per_page=255)
    users = pagination.items
    return render_template('group/details.html', group=cur_group, users=users)
