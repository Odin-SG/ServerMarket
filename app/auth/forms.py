from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from app.models.user import User


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя',
        validators=[
            DataRequired(),
            Length(min=3, max=64),
            Regexp(r'^[A-Za-z0-9_]+$', message='Имя пользователя может содержать только буквы, цифры и _')
        ]
    )
    password = PasswordField('Пароль',
        validators=[
            DataRequired(),
            Length(min=8, max=128)
        ]
    )
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя',
        validators=[
            DataRequired(),
            Length(min=3, max=64),
            Regexp(r'^[A-Za-z0-9_]+$', message='Имя пользователя может содержать только буквы, цифры и _')
        ]
    )
    email = StringField('Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    password = PasswordField('Пароль',
        validators=[
            DataRequired(),
            Length(min=8, max=128)
        ]
    )
    password2 = PasswordField('Повторите пароль',
        validators=[
            DataRequired(),
            EqualTo('password', message='Пароли должны совпадать')
        ]
    )
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Пожалуйста, используйте другое имя пользователя.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Пожалуйста, используйте другой Email.')