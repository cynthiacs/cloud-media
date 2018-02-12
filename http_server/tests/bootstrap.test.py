from app import create_app, db
app = create_app()

"""
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

class LoginForm(Form):
    email = StringField('Email', validators=[Required(),])
    submit = SubmitField('Login')

app = Flask(__name__)
app.config['SECRET_KEY']='yangxudong'

Bootstrap(app)

@app.route('/test')
def home():
    form = LoginForm()
    return render_template('test.html', form=form)
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True, threaded=True)
