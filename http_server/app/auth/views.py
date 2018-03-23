from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm
import json


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        print(request.form["username"])
        print(request.form["password"])
        return redirect(url_for('group.manage'))

    return render_template('auth/login.html')


@auth.route('/login_app', methods=['GET', 'POST'])
def login_app():
    # assert request.method == 'POST'
    action = request.args.get('action', None)
    if action == 'in':
        # data = request.get_data()
        # dict_in = json.loads(data)
        # account = dict_in["account"]
        # password = dict_in["password"]
        # print("LOGIN: account:%s, password:%s" %(account, password))
        dict_return = {"result": "OK", "role": "pusher", "token": "12345678",
                       "vendor_id": "88888888", "vendor_nick": "CM Team",
                       "group_id": "00000000", "group_nick": "Default Group"}
        return json.dumps(dict_return)
    elif action == 'out':
        # data = request.get_data()
        # dict_out = json.loads(data)
        # account = dict_out["account"]
        # print("LOGOUT: account:%s" %(account))

        return json.dumps({"result": "OK"})
    else:
        return json.dumps({"result": "ERROR"})
