from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from app.models.order import OrderStatus


class ChatForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class StatusForm(FlaskForm):
    status = SelectField(
        'Статус заказа',
        choices=[(s.name, s.value) for s in OrderStatus],
        validators=[DataRequired()]
    )
    submit = SubmitField('Обновить статус')
