import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    points = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    problems_status = sqlalchemy.Column(sqlalchemy.String, default="{}")
    notifications = sqlalchemy.Column(sqlalchemy.String, default="[]")
    last_active = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User> {self.id} {self.name} {self.email}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def add_points(self, amount):
        self.points += amount

    def subtract_points(self, amount):
        self.points -= amount

    def add_notification(self, message, problem_id):
        self.notifications = json.loads(self.notifications)
        self.notifications.append(
            (
                datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y"),
                message,
                f"/problem/{problem_id}"
            )
        )
        self.notifications = json.dumps(self.notifications)

    def clear_notifications(self):
        self.notifications = "[]"

    def notifications_count(self):
        return len(json.loads(self.notifications))

    def new_active(self):
        self.last_active = datetime.datetime.now()

    def get_problem_status(self, problem_id):
        if str(problem_id) in json.loads(self.problems_status).keys():
            return json.loads(self.problems_status)[str(problem_id)]
        else:
            return None,

    def set_problem_status(self, problem_id, status, message, code):
        self.problems_status = json.loads(self.problems_status)
        self.problems_status[str(problem_id)] = (status, message, code)
        self.problems_status = json.dumps(self.problems_status)

    def recalculate_points(self, db_sess, problem_class):
        self.points = 0
        solutions_data = json.loads(self.problems_status)
        new_solutions_data = {}

        for i in solutions_data:
            p = db_sess.query(problem_class).filter(problem_class.id == int(i)).first()
            if p:
                new_solutions_data[i] = solutions_data[i]
                if solutions_data[i][0] == "SUCCESS":
                    self.points += p.points

        self.problems_status = json.dumps(new_solutions_data)

        db_sess.commit()
