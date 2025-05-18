from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class QuestionForm(FlaskForm):
    text = TextAreaField('Ваш вопрос', validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField('Задать вопрос')


class AnswerForm(FlaskForm):
    text = TextAreaField('Ваш ответ', validators=[DataRequired(), Length(min=1, max=2000)])
    submit = SubmitField('Ответить')
