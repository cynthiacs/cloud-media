"""

"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, Regexp


class NewGroupForm(FlaskForm):
    """
    NewGroupForm
    """
    gid = StringField('帐号', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                                            '用户名第一个字母必须大写，且只能由字母，'
                                                            '数字，下划线，点组成。')])
    submit = SubmitField('保存')


class EditGroupForm(FlaskForm):
    """
    EditGroupForm
    """
    gid = StringField('帐号', validators=[DataRequired(), Length(1, 64, '长度必须为1-64。')])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                                            '用户名第一个字母必须大写，且只能由字母，'
                                                            '数字，下划线，点组成。')])
    submit = SubmitField('保存')

    def __init__(self, group, *args, **kwargs):
        super(EditGroupForm, self).__init__(*args, **kwargs)
        self.group = group
