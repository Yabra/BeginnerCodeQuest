from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import EmailField, PasswordField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
