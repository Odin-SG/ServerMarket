from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, FormField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from app.models.order import ConfigurationType
from app.models.server import Server


class OrderItemForm(FlaskForm):
    server_id = SelectField('Сервер', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Количество', default=1,
                            validators=[DataRequired(), NumberRange(min=1, max=10)])


class OrderForm(FlaskForm):
    configuration = SelectField('Конфигурация',
                                choices=[(c.name, c.value) for c in ConfigurationType], validators=[DataRequired()])
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    contact_info = TextAreaField('Контактная информация',
                                 validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Оформить заказ')
