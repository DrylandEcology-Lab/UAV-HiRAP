from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField,SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64),
                                             Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1,64), Email()])
    realname = StringField('Real name<font color="red">*</font>', validators=[DataRequired(), Length(1,64)])
    password = PasswordField('Password<font color="red">*</font>', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password<font color="red">*</font>', validators=[DataRequired()])
    country = StringField('Country<font color="red">*</font>', validators=[DataRequired()])
    org = StringField('Organization<font color="red">*</font>', validators=[DataRequired()])
    field = SelectField('Research field<font color="red">*</font>',
                        coerce=int,
                        choices=[(1, 'Earth Science'),
                                 (2, 'Life Science'),
                                 (3, 'Medical Science'),
                                 (4, 'Computer Science'),
                                 (5, 'Chemical Science'),
                                 (6, 'Engineering & Materials'),
                                 (7, 'Other Subject')],
                        validators=[DataRequired()],
                        render_kw={"placeholder": "--select--"})
    major = StringField('Major<font color="red">*</font>', validators=[DataRequired()])
    aim = TextAreaField('Your purpose to use this platform<font color="red">*</font>',
                      validators=[DataRequired()])
    submit = SubmitField('Submit')

    # def __init__(self, *args, **kwargs):
        # in html, {{ form.name_list(placeholder="--select--")}}
        # self.name_list.choices = [(1, '1'),(2, '2'),(3, '3')]

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

class ProfileEditForm(FlaskForm):
    realname = StringField('Real name', validators=[DataRequired(), Length(1, 64)])
    country = StringField('Country', validators=[DataRequired()])
    org = StringField('Organization', validators=[DataRequired()])
    field = SelectField('Research field',
                        coerce=int,
                        choices=[(1, 'Earth Science'),
                                 (2, 'Life Science'),
                                 (3, 'Medical Science'),
                                 (4, 'Computer Science'),
                                 (5, 'Chemical Science'),
                                 (6, 'Engineering & Materials'),
                                 (7, 'Other Subject')],
                        validators=[DataRequired()],
                        render_kw={"placeholder": "--select--"})
    major = StringField('Major', validators=[DataRequired()])
    aim = TextAreaField('Your purpose to use this platform',
                        validators=[DataRequired()])
    submit = SubmitField('Update')
    cancel = SubmitField('Back')