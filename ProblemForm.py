from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import TextAreaField, SubmitField, Label


class ProblemForm(FlaskForm):
    solution = TextAreaField('Решение', validators=[DataRequired()])
    submit = SubmitField('Отправить на проверку')
