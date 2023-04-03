import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    points = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    hours_missing = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        print(f"<User> {self.id} {self.name} {self.email}")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def add_points(self, amount):
        self.points += amount

    def subtract_points(self, amount):
        self.points -= amount

    def add_hours(self, amount):
        self.hours_missing += amount

    def reset_hours_missing(self):
        self.hours_missing = 0
