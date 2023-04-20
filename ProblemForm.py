from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField


class ProblemForm(FlaskForm):
    solution = TextAreaField('Решение')
    solution_file = FileField("solution_file")
    submit = SubmitField('Отправить на проверку')
