/**
 * This is a CloudMedia proxy which provides interface to front-end web applications
 * for communicating with the remote CloudMedia server.
 */

function CMUser(account, password) {
    console.log('CMUser');
    this.account = account;
    this.password = password;
    var _role = '';
    var _token = '';
    var _node_id = '';
    var _vendor_id = '';
    var _vendor_nick = '';
    var _group_id = '';
    var _group_nick = '';

    this.set_user_info = function(user_info) {
        obj = user_info;
        _role = obj.role;
        _token = obj.token;
        _node_id = obj.node_id;
        _vendor_id = obj.vendor_id;
        _vendor_nick = obj.vendor_nick;
        _group_id = obj.group_id;
        _group_nick = obj.group_nick;
    }

    this.print_user_info = function() {
        console.log('UserInfo: role:' + _role + ',token:' + _token + ',nid:' + _node_id + ',vid:' + _vendor_id + ',vnick:' + _vendor_nick + ',gid:' + _group_id + ',gnick:' + _group_nick);
    }

    this.get_role = function() {
        return _role;
    }

    this.get_token = function() {
        return _token;
    }

    this.get_node_id = function() {
        return _node_id;
    }

    this.get_vendor_id = function() {
        return _vendor_id;
    }

    this.get_vendor_nick = function() {
        return _vendor_nick;
    }

    this.get_group_id = function() {
        return _group_id;
    }

    this.get_group_nick = function() {
        return _group_nick;
    }

}

function CMProxy() {
    console.log('CMProxy');
    this.ws_addr = '';
    this.ws = null;
    this.serial = 0;
    this.waiting_replies = {}
    this.sent_requests = {}
    //this.node_info = '';
    this.node_info = '{\"id\":\"N1077746422140\",\"nick\":\"PULLER0\",\"role\":\"puller\",'
      + '\"device_name\":\"default\",\"location\":\"Location Unknown\",\"stream_status\":\"pulling_close\",'
      + '\"vendor_id\":\"V0001\",\"vendor_nick\":\"Leadcore\",\"group_id\":\"G00000\",\"group_nick\":\"Default Group\"}'
    this.on_nodes_update = null;
    this.cm_user = null;

}

CMProxy.prototype.login = function(account, password, listener) {
    this.cm_user = new CMUser(account, password);
    var method = 'Login';
    var params = '{\"account\":\"' + account + '\", \"password\":\"' + password + '\"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype.logout = function(account, listener) {
    var method = 'Logout';
    var params = '{\"account\":\"' + account + '\"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype._connect = function(host, port) {
    var ws_addr = "ws://" + host + ":" + port
    this.ws = new WebSocket(ws_addr)

    this.ws.onopen = this._onopen
    this.ws.onclose = this._onclose
    this.ws.onmessage = this._onmessage
    this.ws.onerror = this._onerror
}   

CMProxy.prototype.set_onopen = function(foo) {
    console.log('set onopen');
    this.ws.onpen = foo
}

CMProxy.prototype.set_onclose = function(foo) {
    console.log('set onclose');
    this.ws.onclose = foo
}

CMProxy.prototype.set_onmessage = function(foo) {
    console.log('set onmessage');
    this.ws.onmessage = foo
}

CMProxy.prototype.set_onerror = function(foo) {
    console.log('set onerror');
    this.ws.onerror = foo
}

CMProxy.prototype.set_nodes_update_listener = function(listener) {
    this.on_nodes_update = listener;
}

CMProxy.prototype._send_request = function(method, params, listener) {
    var request = '{\"jsonrpc\":2.0, \"method\":\"' + method + '\",\"params\":' + params + ',\"id\":\"' + this.serial + '\"}';
    console.log(request)

    this.ws.send(request);
    this.waiting_replies[this.serial] = listener
    console.log('add listener to waiting replies')
    console.log(this.waiting_replies)
    this.sent_requests[this.serial] = method
    console.log('add method to sent requests')
    console.log(this.sent_requests)

    ++this.serial;
}

CMProxy.prototype.set_node_info = function(info) {
    this.node_info = info
}

CMProxy.prototype.connect_mc = function() {
    console.log('connect_mc');
}

CMProxy.prototype.connect = function(listener) {
    var method = 'Connect'
    var params = this.node_info; //get when login 
    this._send_request(method, params, listener);
}

CMProxy.prototype.disconnect = function(listener) {
    var method = 'Disconnect'
    var params = this.node_info; //get when login 
    this._send_request(method, params, listener);
}

CMProxy.prototype.start_video = function(target_tag, expire_time, listener) {
    var method = 'StartPushMedia'
    var params = '{"target-id":"' + target_tag + '","expire-time":"' + expire_time + 's"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype.stop_video = function(target_tag, expire_time, listener) {
    method = 'StopPushMedia'
    var params = '{"target-id":"' + target_tag + '","expire-time":"' + expire_time + 's"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype._onopen = function() {
    console.log('onopen');
}

CMProxy.prototype._onclose = function() {
    console.log('onclose');
}

CMProxy.prototype._handle_reply = function(jrpc) {
    var id = jrpc["id"];
    var listener = cmproxy.waiting_replies[id];
    if (listener == null) {
        console.log('unknown reply?');
        return;
    }

    if ('error' in jrpc) {
        var text = '{\"error\":' + JSON.stringify(jrpc["error"]) + '}';
        listener(text);
    } else if ('result' in jrpc) {

        if(id in cmproxy.waiting_replies) {
            console.log('id is found in waiting replies');
            var request = cmproxy.sent_requests[id];
            var result = jrpc["result"];
            switch(request) {
            case 'Login':
                cmproxy.cm_user.set_user_info(result);
                cmproxy.cm_user.print_user_info();
            default:
                var text = '{\"result\":' + JSON.stringify(jrpc["result"]) + '}';
                listener(text);
                break;
            }
        }
    } else {
        console.log('unknown waiting replies for id:' + id);
    }

    delete cmproxy.waiting_replies[id];
    delete cmproxy.sent_requests[id];
}

CMProxy.prototype._handle_notify = function(jstr) {

}

CMProxy.prototype._onmessage = function(evt) {
    console.log('onmessage:' + evt.data + ', type:' + typeof(evt.data));
    if(evt.data[0] == '{' || evt.data[0] == "\'") {
        payload = evt.data;
    } else {
        // the string from mg looks like:
        // b'{"jsonrpc": "2.0", "result": "OK", "id": "4"}'
        // this is a workroud before fix
        payload = evt.data.slice(2, -1);
    }

    var jrpc = JSON.parse(payload.toString())
    if('all_online' in jrpc || 'new_online' in jrpc
        || 'new_offline' in jrpc || 'new_update' in jrpc) {
        console.log('online nodes info changed')
        if(this.on_nodes_update != null) {
            this.on_nodes_update(jrpc);
        }
    }

    if('id' in jrpc) {
        //this._handle_reply(jrpc);
        cmproxy._handle_reply(jrpc);
    }
}

CMProxy.prototype._onerror = function(error) {
    console.log('onerror');
}

cmproxy = new CMProxy();
cmproxy._connect('127.0.0.1', '9001')

