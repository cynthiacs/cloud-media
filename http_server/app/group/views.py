"""

"""
from flask import url_for, redirect, render_template, request, flash

from .. import messages
from . import group
from .forms import NewGroupForm, EditGroupForm
from ..models import CmGroup


@group.route('/group/new', methods=['GET', 'POST'])
def new():
    """
    new one group
    :return:
    """
    print(request.method)
    form = NewGroupForm()
    if form.validate_on_submit():
        new_group = CmGroup()
        new_group.gid = form.gid.data
        new_group.username = form.username.data
        new_group.save()
        return redirect(url_for('group.manage'))
    return render_template('group/new.html', form=form)


@group.route('/group/edit/<gid>', methods=['GET', 'POST'])
def edit(gid):
    """
    edit the name gid of group
    :param gid:
    :return:
    """
    cur_group = CmGroup.objects.get_or_404(gid=gid)
    form = EditGroupForm(cur_group)
    if form.validate_on_submit():
        cur_group.username = form.username.data
        cur_group.update(username=form.username.data)
        return redirect(url_for('group.manage'))
    form.gid.data = cur_group.gid
    form.username.data = cur_group.username

    return render_template('group/edit.html', form=form, group=group)


@group.route('/group/delete/<gid>')
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
    return redirect(url_for('group.manage'))


@group.route('/group/manage')
def manage():
    """
    group manage table data from db
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = CmGroup.objects.paginate(page=page, per_page=255)
    groups = pagination.items
    return render_template('group/manage.html', groups=groups)
