from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, URL, NumberRange, Regexp, Email, Optional, ValidationError
from flask_wtf.file import FileField
from app.models.server import Server
from app.models.order import OrderStatus
from app.models.user import UserRole
from flask import current_app
import json

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class ServerForm(FlaskForm):
    model_name = StringField('Модель', validators=[DataRequired(), Length(3, 100)])
    slug = StringField('Slug', validators=[DataRequired(), Length(3, 120), Regexp(r'^[a-z0-9-]+$')])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(min=10)])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)], places=2)
    specifications = TextAreaField('Характеристики (JSON)', validators=[Length(max=2000)])
    image_url = StringField('URL изображения', validators=[Optional(), URL()])
    image_file = FileField('Файл изображения')
    use_upload = BooleanField('Загрузить изображение с компьютера')
    replace_image = BooleanField('Заменить изображение')
    use_upload = BooleanField('  • как файл (если не отмечено — оставляем старое)')
    is_available = BooleanField('В наличии')
    quantity = IntegerField('Количество на складе', validators=[DataRequired(), NumberRange(min=0)], default=0)
    submit = SubmitField('Сохранить')

    def validate_slug(self, field):
        existing = Server.query.filter_by(slug=field.data).first()
        original = getattr(self, 'original_slug', None)
        if existing and field.data != original:
            raise ValidationError('Slug уже используется')

    def validate_specifications(self, field):
        if field.data:
            try:
                json.loads(field.data)
            except:
                raise ValidationError('Неверный JSON')

    def validate_image_url(self, field):
        if self.replace_image.data and not self.use_upload.data and not field.data:
            raise ValidationError('Укажите новый URL или загрузите файл.')

    def validate_image_file(self, field):
        if self.replace_image.data and self.use_upload.data:
            if not field.data or not getattr(field.data, 'filename', None):
                raise ValidationError('Загрузите файл изображения.')


class OrderEditForm(FlaskForm):
    status = SelectField(
        'Статус заказа',
        choices=[(s.name, s.value) for s in OrderStatus],
        validators=[DataRequired()]
    )
    contact_info = TextAreaField(
        'Контактная информация',
        validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField('Сохранить изменения')


class ChatMessageEditForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=2000)])
    save = SubmitField('Сохранить')
    delete = SubmitField('Удалить')


class UserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('Имя', validators=[Optional(), Length(max=30)])
    last_name = StringField('Фамилия', validators=[Optional(), Length(max=30)])
    phone_number = StringField('Телефон', validators=[Optional(), Length(max=20)])
    avatar_url = StringField('URL аватара', validators=[Optional(), URL()])
    address = TextAreaField('Адрес', validators=[Optional(), Length(max=500)])
    role = SelectField(
        'Роль',
        choices=[(r.name, r.value) for r in UserRole],
        validators=[DataRequired()]
    )
    is_active = BooleanField('Активен')
    submit = SubmitField('Сохранить изменения')


class ReportUserForm(FlaskForm):
    user_id = SelectField(
        'Пользователь',
        coerce=int,
        validators=[DataRequired()],
        choices=[]
    )
    submit = SubmitField('Сформировать отчёт')


class ReportServerForm(FlaskForm):
    server_id = SelectField(
        'Сервер',
        coerce=int,
        validators=[DataRequired()],
        choices=[]
    )
    submit = SubmitField('Сформировать отчёт')
