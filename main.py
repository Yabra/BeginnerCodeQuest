import datetime
import random
import json
from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

import ProblemStatusTypes
from data import db_session
from data.user import User
from data.problem import Problem
from LoginForm import LoginForm
from RegisterForm import RegisterForm
from ProblemForm import ProblemForm
from testing_connect import ResultResource, new_request, init
from mail_notification import notification_in_thread

app = Flask(__name__)
api = Api(app)
api.add_resource(ResultResource, "/api/results")

app.config['SECRET_KEY'] = "yabrortus"

cnf_file = open("./config/main.json")
cnf_data = json.loads(cnf_file.read())
cnf_file.close()

app.config['HOST'] = cnf_data["host"]
app.config['PORT'] = cnf_data["port"]
app.config['TESTING_SERVER_ADDRESS'] = cnf_data["testing_server_address"]

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/db.db")
db_sess = db_session.create_session()
init(db_sess, app)


def get_rating_table():
    table = []
    for user in db_sess.query(User):
        table.append((user.name, user.points))

    table.sort(key=lambda x: x[1], reverse=True)

    table = [(i + 1, elem) for i, elem in enumerate(table)]
    return table


def get_notifications():
    notifications_list = json.loads(current_user.notifications)
    notifications_list = sorted(notifications_list,
                                key=lambda x: datetime.datetime.strptime(x[0], "%H:%M:%S %d.%m.%Y"),
                                reverse=True)
    return notifications_list


def get_problem_statuses():
    problem_statuses = json.loads(current_user.problems_status)
    return problem_statuses


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


@app.route('/problems_list')
def problems_list():
    check_user_activity()
    return render_template('problems_list.html', title="Список задач", problems=db_sess.query(Problem))


@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem_page(problem_id):
    check_user_activity()

    if problem_id > db_sess.query(Problem).count():
        return page_not_found(None)

    form = ProblemForm()
    current_problem = get_problem(problem_id)

    if request.method == "POST" and "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        form.solution.data = file.stream.read().decode()
        if not form.solution.data:
            return render_template('problem.html', title=f"Задача №{None}",
                                   form=form,
                                   current_problem=current_problem,
                                   message="Вы не можете отослать пустое решение!")
        new_request(current_user, current_problem, form.solution.data)

    elif form.validate_on_submit():
        if not form.solution.data:
            return render_template('problem.html', title=f"Задача \"{current_problem.name}\"",
                                   form=form,
                                   current_problem=current_problem)
        new_request(current_user, current_problem, form.solution.data)

    elif current_user.is_authenticated and current_user.get_problem_status(problem_id)[0]:
        form.solution.data = current_user.get_problem_status(problem_id)[2]

    return render_template('problem.html', title=f"Задача \"{current_problem.name}\"",
                           form=form,
                           current_problem=current_problem)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
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
    if current_user.is_authenticated:
        return redirect("/")
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


@app.route('/next_problem')
@login_required
def next_problem():
    problems = [str(i) for i in range(1, db_sess.query(Problem).count() + 1)]
    for problem_id, status in get_problem_statuses().items():
        if status[0] == ProblemStatusTypes.SUCCESS:
            problems.remove(problem_id)

    if not problems:
        return redirect("/problems_list")

    return redirect(f"/problem/{random.choice(problems)}")


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
    notification_in_thread(db_sess)
    app.run(port=app.config["PORT"], host=app.config["HOST"])
