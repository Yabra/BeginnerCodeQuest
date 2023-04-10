import sqlalchemy
from .db_session import SqlAlchemyBase


class Problem(SqlAlchemyBase):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    tests = sqlalchemy.Column(sqlalchemy.String)
    points = sqlalchemy.Column(sqlalchemy.Integer)
