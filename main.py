from random import randint
import json
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.user import User
from data.problem import Problem
from LoginForm import LoginForm
from RegisterForm import RegisterForm
from ProblemForm import ProblemForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yabrortus'
login_manager = LoginManager()
login_manager.init_app(app)

rating_table = None


def update_rating_table():
    global rating_table
    db_sess = db_session.create_session()
    rating_table = []
    for user in db_sess.query(User):
        rating_table.append((user.name, user.points))

    rating_table.sort(key=lambda x: x[1], reverse=True)

    rating_table = [(i + 1, elem) for i, elem in enumerate(rating_table)]


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@login_manager.user_loader
def get_problem(problem_id):
    db_sess = db_session.create_session()
    return db_sess.query(Problem).filter(Problem.id == problem_id).first()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Главная")


@app.route('/about')
def about():
    return render_template('about.html', title="Об сайте")


@app.route('/profile')
def profile():
    return render_template('profile.html', title="Профиль")


@app.route('/rating')
def rating():
    return render_template('rating.html', title="Таблица рейтинга", rating_table=rating_table)


@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem(problem_id):
    db_sess = db_session.create_session()
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
        print(form.solution.data)

    return render_template('problem.html', title=f"Задача №{None}", form=form, current_problem=current_problem)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
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
        update_rating_table()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/next_problem/<difficulty>')
@login_required
def next_problem(difficulty):
    db_sess = db_session.create_session()
    return redirect(f"/problem/{randint(0, db_sess.query(Problem).count())}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    db_session.global_init("db/db.db")
    db_sess = db_session.create_session()
    new_problem = Problem(
        name="Скажи привет!",
        description="<p>Создайте программу, принимающую строку и здоровающуся с пользователем.</p>"
                    "<h4>Пример:<h4>"
                    "<p><t>Ввод:</p>"
                    "<p><i>Vlad</i></p>"
                    "<p>    Вывод:</p>"
                    "<p><i>Hello, Vlad!</i></p>",
        tests=json.dumps(
            [("Ярослав", "Hello, Ярослав!\n"), ("Влад", "Hello, Влад!\n"), ("Pavel", "Hello, Pavel!\n")]
        ),
        difficulty=0,
        points=5
    )
    db_sess.add(new_problem)
    db_sess.commit()

    update_rating_table()
    app.run(port=8080, host='127.0.0.1')
