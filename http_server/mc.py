from app import create_app, db, mqtt
from config import config

app = create_app()

if __name__ == '__main__':
    app.run(host=config['flask_app']['host'], port=config['flask_app']['port'], debug=True, threaded=True, use_reloader=False)
