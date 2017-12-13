from flask import Flask
from flask import request

app = Flask(__name__)

_ID = 0


@app.route('/get_id')
def get_id():
    global _ID
    _ID += 1
    return str(_ID)


@app.route('/cm_live_steams_notify')
def cm_live_steams_notify():
    print(request.data)
    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)