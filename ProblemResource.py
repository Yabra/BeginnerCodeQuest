import json
from flask import request
from flask_restful import Resource
from data.problem import Problem
from data.user import User


class ProblemResource(Resource):
    db_sess = None
    password = None

    def get(self):
        id = request.args.get("id")
        if not id:
            problems = ProblemResource.db_sess.query(Problem)
            return_dict = {}
            for p in problems:
                return_dict[p.id] = {"name": p.name, "description": p.description, "tests": p.tests, "points": p.points}
            return return_dict
        else:
            p = ProblemResource.db_sess.query(Problem).filter(Problem.id == id).first()
            if p:
                return {p.id: {"name": p.name, "description": p.description, "tests": p.tests, "points": p.points}}
            else:
                return {"message": f"Problem with id {id} not exists!"}

    def post(self):
        try:
            json_data = json.loads(request.get_json())
            if ProblemResource.password != json_data["password"]:
                return {"message": "Uncorrect developer password!"}

            new_problem = Problem(
                name=json_data["name"],
                description=json_data["description"],
                tests=json_data["tests"],
                points=json_data["points"],
            )
            ProblemResource.db_sess.add(new_problem)
            ProblemResource.db_sess.commit()
            return {"message": "ok"}

        except Exception:
            return {"message": "Bad request!"}

    def delete(self):
        if ProblemResource.password != request.args.get("password"):
            return {"message": "Uncorrect developer password!"}

        id = request.args.get("id")

        if id:
            ProblemResource.db_sess.query(Problem).filter(Problem.id == id).delete()
            ProblemResource.db_sess.commit()

            users = ProblemResource.db_sess.query(User)

            for u in users:
                u.recalculate_points(ProblemResource.db_sess, Problem)

            return {"message": "ok"}

        return {"message": "Bad request!"}


def init(db_sess, password):
    ProblemResource.db_sess = db_sess
    ProblemResource.password = password
