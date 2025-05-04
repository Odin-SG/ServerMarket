from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, URL, NumberRange, Regexp, Optional, ValidationError
from app.models.server import Server
import json


class ServerForm(FlaskForm):
    model_name = StringField('Модель', validators=[DataRequired(), Length(3, 100)])
    slug = StringField('Slug', validators=[DataRequired(), Length(3, 120), Regexp(r'^[a-z0-9-]+$')])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(min=10)])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)], places=2)
    specifications = TextAreaField('Характеристики (JSON)', validators=[Length(max=2000)])
    image_url = StringField('URL изображения', validators=[Optional(), URL()])
    is_available = BooleanField('В наличии')
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
