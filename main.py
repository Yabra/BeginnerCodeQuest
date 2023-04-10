import datetime
from random import randint
import json
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from data import db_session
from data.user import User
from data.problem import Problem
from LoginForm import LoginForm
from RegisterForm import RegisterForm
from ProblemForm import ProblemForm
from testing_connect import SolutionResource, new_request, init


app = Flask(__name__)
api = Api(app)
api.add_resource(SolutionResource, '/api/solution_testing')

app.config['SECRET_KEY'] = 'yabrortus'
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/db.db")
db_sess = db_session.create_session()
init(db_sess)


def get_rating_table():
    table = []
    for user in db_sess.query(User):
        table.append((user.name, user.points))

    table.sort(key=lambda x: x[1], reverse=True)

    table = [(i + 1, elem) for i, elem in enumerate(table)]
    return table


def get_notifications():
    notifications = json.loads(current_user.notifications)
    notifications = sorted(notifications,
                           key=lambda x: datetime.datetime.strptime(x[0], "%H:%M:%S %d.%m.%Y"),
                           reverse=True)
    return notifications


def check_user_activity():
    if current_user.is_authenticated:
        current_user.new_active()
        db_sess.add(current_user)
        db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    user = db_sess.query(User).get(user_id)
    return user


def get_problem(problem_id):
    problem = db_sess.query(Problem).get(problem_id)
    return problem


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Главная")


@app.route('/about')
def about():
    check_user_activity()
    return render_template('about.html', title="Об сайте")


@app.route('/profile')
def profile():
    check_user_activity()
    return render_template('profile.html', title="Профиль")


@app.route('/rating')
def rating():
    check_user_activity()
    return render_template('rating.html', title="Таблица рейтинга", rating_table=get_rating_table())


@app.route('/notifications')
def notifications():
    check_user_activity()
    return render_template('notifications.html', title="Уведомления", notifications=get_notifications())


@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem_page(problem_id):
    check_user_activity()

    if problem_id > db_sess.query(Problem).count():
        return page_not_found(None)

    form = ProblemForm()
    current_problem = get_problem(problem_id)
    if form.validate_on_submit():
        if not form.solution.data:
            return render_template('problem.html', title=f"Задача №{None}",
                                   form=form,
                                   current_problem=current_problem,
                                   message="Вы не можете отослать пустое решение!")
        new_request(current_user, current_problem, form.solution.data)
    else:
        if current_user.is_authenticated and current_user.get_problem_status(problem_id)[0]:
            form.solution.data = current_user.get_problem_status(problem_id)[2]
    return render_template('problem.html', title=f"Задача \"{current_problem.name}\"", form=form, current_problem=current_problem)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=False)
        check_user_activity()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            check_user_activity()
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    check_user_activity()
    logout_user()
    return redirect("/")


@app.route('/clear_notifications')
@login_required
def clear_notifications():
    current_user.clear_notifications()
    db_sess.add(current_user)
    db_sess.commit()
    check_user_activity()
    return redirect("/notifications")


@app.route('/next_problem/<difficulty>')
@login_required
def next_problem(difficulty):
    problem_id = randint(0, db_sess.query(Problem).count())
    return redirect(f"/problem/{problem_id}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # new_problem = Problem(
    #     name="Скажи привет!",
    #     description="<p>Создайте программу, принимающую строку и здоровающуся с пользователем.</p>"
    #                 "<h4>Пример:<h4>"
    #                 "<p><t>Ввод:</p>"
    #                 "<p><i>Vlad</i></p>"
    #                 "<p>    Вывод:</p>"
    #                 "<p><i>Hello, Vlad!</i></p>",
    #     tests=json.dumps(
    #         [("Ярослав", "Hello, Ярослав!\n"), ("Влад", "Hello, Влад!\n"), ("Pavel", "Hello, Pavel!\n")]
    #     ),
    #     difficulty=0,
    #     points=5
    # )
    # db_sess.add(new_problem)
    # db_sess.commit()

    app.run(port=8080, host='127.0.0.1')
