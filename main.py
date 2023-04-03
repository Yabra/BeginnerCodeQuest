from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.user import User
from LoginForm import LoginForm
from RegisterForm import RegisterForm


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


if __name__ == '__main__':
    db_session.global_init("db/db.db")
    update_rating_table()
    app.run(port=8080, host='127.0.0.1')
