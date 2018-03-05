from app import create_app, db, mqtt

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True, use_reloader=False)
