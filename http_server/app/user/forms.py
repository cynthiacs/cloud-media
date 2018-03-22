"""

"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import Length, DataRequired, Regexp, EqualTo


class NewUserForm(FlaskForm):
    """
    NewUserForm
    """
    account = StringField('帐号', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                                            '用户名第一个字母必须大写，且只能由字母，'
                                                            '数字，下划线，点组成。')])
    active = BooleanField('激活')
    role = SelectField('角色')
    group = SelectField('组')
    password = PasswordField('密码', validators=[
        DataRequired(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                                            '密码第只能由字母，数字，下划线，点组成。')])
    password_verify = PasswordField('确认密码', validators=[
        DataRequired(), Length(1, 16, '长度必须为1-16。'), EqualTo('password', '必须和密码一致。')])
    vendor = StringField('Vendor', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])

    submit = SubmitField('保存')

    def __init__(self, groups, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [('puller', 'Puller'), ('pusher', 'Pusher')]
        groupsList = []
        for group in groups:
            groupsList.append((group.gid, group.username))
        self.group.choices = groupsList


class EditUserForm(FlaskForm):
    """
    EditUserForm
    """
    account = StringField('帐号', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                                            '用户名第一个字母必须大写，且只能由字母，'
                                                            '数字，下划线，点组成。')])
    active = BooleanField('激活')
    role = SelectField('角色')
    group = SelectField('组')
    password = PasswordField('密码', validators=[
        DataRequired(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                                            '密码第只能由字母，数字，下划线，点组成。')])
    password_verify = PasswordField('确认密码', validators=[
        DataRequired(), Length(1, 16, '长度必须为1-16。'), EqualTo('password', '必须和密码一致。')])
    vendor = StringField('Vendor', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])

    submit = SubmitField('保存')

    def __init__(self, user, groups, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [('puller', 'Puller'), ('pusher', 'Pusher')]
        groupsList = []
        for group in groups:
            groupsList.append((group.gid, group.username))
        self.group.choices = groupsList
        self.user = user
