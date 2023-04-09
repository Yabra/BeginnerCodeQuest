from flask_restful import reqparse, Resource
from flask import request
from data.user import User
from data.problem import Problem
import json
import uuid
import requests
from sqlalchemy.orm import Session


test_requests = {}

db_sess: Session = None


def init(db):
    global db_sess
    db_sess = db


def new_request(user: User, problem: Problem, code: str):
    new_uuid = uuid.uuid4()
    test_requests[str(new_uuid)] = (user.id, problem)
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
            if json_data["result"] == "SUCCESS":
                user = db_sess.query(User).get(test_requests[json_data["uuid"]][0])
                user.points += test_requests[json_data["uuid"]][1].points

                user.add_notification("Решено!", test_requests[json_data["uuid"]][1].id)

                db_sess.add(user)
                db_sess.commit()
        return json.dumps({'success': 'OK'})
