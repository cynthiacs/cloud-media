from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class NewUserForm(FlaskForm):
    uid = StringField('User ID', validators=[Length(0, 64)])
    account = StringField('Account', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[Length(0, 64)])

    email = StringField('Email', validators=[Length(1, 64), Email()])
    role = SelectField('Role')
    group = SelectField('Group')
    confirmed_at = DateTimeField('Confirmed Time')
    active = BooleanField('active')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [("puller", "Puller"), ("pusher", "Pusher")]
        self.group.choices = [("G000000", "Group 0"), ("G000001", "Group 1")]
