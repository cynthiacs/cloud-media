import datetime

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user

from .. import messages
from . import auth
from ..models import User, Vendor, db_setting
import json


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # db_setting(host='localhost', port=27017, database='usermanager')
        vendor = Vendor.objects(username=request.form["username"]).first()

        if vendor is not None:
            if vendor.verify_password(request.form["password"]):
                remember_me = False
                if "remember" in json.dumps(request.form):
                    remember_me = True

                # if current_user.is_authenticated:
                #    flash(messages.user_login_already)
                # else:
                login_user(vendor, remember=remember_me, duration=datetime.timedelta(minutes=30))
                return redirect(request.args.get('next') or url_for('group.manage'))
            else:
                flash(messages.wrong_username_password)
        else:
            flash(messages.user_not_found)

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/login.html')


@auth.route('/login_app', methods=['GET', 'POST'])
def login_app():
    # assert request.method == 'POST'
    action = request.args.get('action', None)
    if action == 'in':
        data = request.get_data()
        dict_in = json.loads(data)
        account = dict_in['account']
        password = dict_in['password']
        print("LOGIN: account:%s, password:%s" % (account, password))

        cur_user = User.objects(account=account).first()
        if cur_user is None:
            return json.dumps({'result': 'ERROR'})
        if password != cur_user.password:
            return json.dumps({'result': 'ERROR'})
        user_info_seq = ('result', 'role', 'token', 'vendor_id', 'vendor_nick', 'group_id', 'group_nick')
        dict_return = dict.fromkeys(user_info_seq)
        dict_return['result'] = 'OK'
        dict_return['role'] = cur_user.role
        dict_return['token'] = cur_user.token
        dict_return['vendor_id'] = cur_user.vid
        dict_return['vendor_nick'] = cur_user.vendor
        dict_return['group_id'] = cur_user.group.gid
        dict_return['group_nick'] = cur_user.group.name

        # dict_return = {"result": "OK", "role": "pusher", "token": "12345678",
        #               "vendor_id": "88888888", "vendor_nick": "CM Team",
        #               "group_id": "00000000", "group_nick": "Default Group"}
        return json.dumps(dict_return)
    elif action == 'out':
        data = request.get_data()
        dict_out = json.loads(data)
        account = dict_out["account"]
        print("LOGOUT: account:%s" % (account))

        cur_user = User.objects(account=account).first()
        if cur_user is None:
            return json.dumps({'result': 'ERROR'})

        return json.dumps({'result': 'OK'})
    else:
        return json.dumps({'result': 'ERROR'})
