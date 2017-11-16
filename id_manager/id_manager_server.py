from flask import Flask
app = Flask(__name__)

_ID = 0

@app.route('/get_id')
def get_id():
    global _ID
    _ID += 1
    return str(_ID)
