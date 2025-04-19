from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, URL, NumberRange, ValidationError, Regexp, Optional
from app.models.server import Server
import re

class ServerForm(FlaskForm):
    model_name = StringField(
        'Модель',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    slug = StringField(
        'URL Slug',
        validators=[DataRequired(), Length(min=3, max=120),
                    Regexp(r'^[a-z0-9-]+$', message='Только строчные латинские, цифры и дефис')]
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

    def validate_slug(self, slug):
        if Server.query.filter_by(slug=slug.data).first():
            raise ValidationError('Slug уже используется.')

    def validate_specifications(self, specifications):
        if specifications.data:
            try:
                import json
                json.loads(specifications.data)
            except json.JSONDecodeError:
                raise ValidationError('Недействительный JSON.')