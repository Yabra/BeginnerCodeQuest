from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ProblemForm(FlaskForm):
    solution = TextAreaField('Решение', validators=[DataRequired()])
    submit = SubmitField('Отправить на проверку')
