import sqlalchemy
from .db_session import SqlAlchemyBase
import json


class Problem(SqlAlchemyBase):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    tests = sqlalchemy.Column(sqlalchemy.String, unique=True)
    difficulty = sqlalchemy.Column(sqlalchemy.Integer)
    points = sqlalchemy.Column(sqlalchemy.Integer)

    def parse_tests(self, js) -> dict:
        d = json.loads(js)
        return d

    def set_name(self, name):
        pass

    def set_difficulty(self, dif):
        pass

    def set_tests(self, tests: str):
        pass

    def set_points(self, pts):
        pass


