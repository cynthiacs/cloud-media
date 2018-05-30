
function CMProxy() {
    console.log('CMProxy');
    this.host = ''; 
    this.port = ''; 
    this.ws_addr = '';
    this.ws = null;
    this.serial = 0;
    this.waiting_replies = {}
    this.pending_requests = []
    //this.node_info = '';
    this.node_info = '{\"id\":\"N1077746422140\",\"nick\":\"PULLER0\",\"role\":\"puller\",'
      + '\"device_name\":\"default\",\"location\":\"Location Unknown\",\"stream_status\":\"pulling_close\",'
      + '\"vendor_id\":\"V0001\",\"vendor_nick\":\"Leadcore\",\"group_id\":\"G00000\",\"group_nick\":\"Default Group\"}'

}

CMProxy.prototype.connect = function(host, port) {
    this.host = host
    this.port = port
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

CMProxy.prototype._send_request = function(method, params, listener) {
    var request = '{\"jsonrpc\":2.0, \"method\":\"' + method + '\",\"params\":' + params + ',\"id\":\"' + this.serial + '\"}';
    console.log(request)

    this.ws.send(request);
    this.waiting_replies[this.serial] = listener
    console.log('add listener to waiting replies')
    console.log(this.waiting_replies)

    ++this.serial;
}

CMProxy.prototype.login = function(account, psw, listener) {
    var method = 'Login';
    var params = '{\"account\":\"' + account + '\", \"password\":\"' + psw + '\"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype.connect_mc = function() {
    console.log('connect_mc');
}

CMProxy.prototype.online = function(listener) {
    var method = 'Online'
    var params = this.node_info; //get when login 
    this._send_request(method, params, listener);
}

CMProxy.prototype.offline = function(listener) {
    var method = 'Offline'
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

CMProxy.prototype.logout = function(account, psw, listener) {
    var method = 'Logout';
    var params = '{\"account\":\"' + account + '\", \"password\":\"' + psw + '\"}'
    this._send_request(method, params, listener);
}

CMProxy.prototype._onopen = function() {
    console.log('onopen');
}

CMProxy.prototype._onclose = function() {
    console.log('onclose');
}

CMProxy.prototype._onmessage = function(evt) {
    console.log('onmessage:' + evt.data);
    var jrpc = JSON.parse(evt.data)
    var id = jrpc["id"]
    console.log(cmproxy.waiting_replies)

    if(cmproxy.waiting_replies != null) {
        if(id in cmproxy.waiting_replies) {
            console.log('id is found in waiting replies')
            cmproxy.waiting_replies[id](evt.data)
            delete cmproxy.waiting_replies[id]
        }
    } else {
        console.log('no waiting replies for id:' + id)
    }
}

CMProxy.prototype._onerror = function(error) {
    console.log('onerror');
}

cmproxy = new CMProxy();
cmproxy.connect('139.224.128.15', '9001')

