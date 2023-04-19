import json
import uuid

import requests
from flask import request
from flask_restful import Resource
from sqlalchemy.orm import Session

import ProblemStatusTypes
from data.problem import Problem
from data.user import User

test_requests = {}

db_sess: Session = None


def init(db):
    global db_sess
    db_sess = db


def new_request(user: User, problem: Problem, code: str):
    if user.get_problem_status(problem.id)[0] == ProblemStatusTypes.SUCCESS:
        return

    new_uuid = uuid.uuid4()
    test_requests[str(new_uuid)] = (user.id, problem, code)
    requests.post(
        "http://127.0.0.1:5000/get_solution_data",
        json=json.dumps(
            {"uuid": str(new_uuid), "code": code, "tests": problem.tests}
        )
    )


class SolutionResource(Resource):
    def post(self):
        global db_sess
        json_data = json.loads(request.get_json())

        if json_data["uuid"] in test_requests.keys():
            request_data = test_requests[json_data["uuid"]]
            user: User = db_sess.query(User).get(test_requests[json_data["uuid"]][0])
            problem: Problem = request_data[1]

            user.set_problem_status(problem.id, json_data["status"], json_data["msg"], request_data[2])

            if json_data["status"] == ProblemStatusTypes.SUCCESS:
                user.points += problem.points
                user.add_notification("Решено!", problem.id)

            elif json_data["status"] == ProblemStatusTypes.WRONG:
                user.add_notification("Неверный ответ!", problem.id)

            elif json_data["status"] == ProblemStatusTypes.EXCEPTION:
                user.add_notification("Ошибка!", problem.id)

            elif json_data["status"] == ProblemStatusTypes.TIME_LIMIT:
                user.add_notification("Слишком медленное решение!", problem.id)

            elif json_data["status"] == ProblemStatusTypes.SYNTAX_ERROR:
                user.add_notification("Синтаксическая ошибка!", problem.id)

            db_sess.add(user)
            db_sess.commit()
