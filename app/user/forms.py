from flask_wtf import FlaskForm
from wtforms import (
    SelectField, FieldList, FormField, IntegerField,
    TextAreaField, SubmitField, PasswordField,
    StringField, DecimalField, BooleanField
)
from wtforms.validators import (
    DataRequired, NumberRange, Length, URL,
    ValidationError, Regexp, Optional, Email, EqualTo
)
from app.models.order import ConfigurationType
from app.models.server import Server
import json


class OrderItemForm(FlaskForm):
    class Meta:
        csrf = False

    server_id = SelectField('Сервер', coerce=int, validators=[DataRequired()])
    quantity = IntegerField(
        'Количество',
        default=1,
        validators=[DataRequired(), NumberRange(min=1, max=10)]
    )


class OrderForm(FlaskForm):
    configuration = SelectField('Конфигурация', validators=[DataRequired()])
    contact_info = TextAreaField(
        'Контактная информация',
        validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField('Оформить заказ')


class ServerForm(FlaskForm):
    model_name = StringField(
        'Модель',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    slug = StringField(
        'URL Slug',
        validators=[
            DataRequired(),
            Length(min=3, max=120),
            Regexp(r'^[a-z0-9-]+$', message='Только строчные латинские, цифры и дефис')
        ]
    )
    description = TextAreaField(
        'Описание',
        validators=[DataRequired(), Length(min=10)]
    )
    price = DecimalField(
        'Цена (₽)',
        validators=[DataRequired(), NumberRange(min=0)],
        places=2
    )
    specifications = TextAreaField(
        'Характеристики (JSON)',
        validators=[Length(max=2000)]
    )
    image_url = StringField(
        'URL изображения',
        validators=[Length(max=255), Optional(), URL(message='Недействительный URL')]
    )
    is_available = BooleanField('В наличии')
    submit = SubmitField('Сохранить')

    def validate_slug(self, field):
        if Server.query.filter_by(slug=field.data).first():
            raise ValidationError('Slug уже используется.')

    def validate_specifications(self, field):
        if field.data:
            try:
                json.loads(field.data)
            except json.JSONDecodeError:
                raise ValidationError('Недействительный JSON.')


class CartCheckoutForm(FlaskForm):
    contact_info = TextAreaField(
        'Контактная информация',
        validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField('Оформить заказ')


class UserSettingsForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('Имя', validators=[Optional(), Length(max=30)])
    last_name = StringField('Фамилия', validators=[Optional(), Length(max=30)])
    phone_number = StringField('Телефон', validators=[Optional(), Length(max=20)])
    avatar_url = StringField('URL аватара', validators=[Optional(), URL()])
    address = TextAreaField('Адрес', validators=[Optional(), Length(max=500)])
    change_password = BooleanField('Сменить пароль')
    password = PasswordField('Новый пароль', validators=[Optional(), Length(min=6)])
    confirm = PasswordField('Повтор пароля',
                            validators=[Optional(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Сохранить изменения')
