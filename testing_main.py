import json
import os

import flask
from flask import Flask, jsonify, request
from flask_restful import Api
from flask_restful import Resource, reqparse

from testing import run_code


class SolutionResource(Resource):
    def post(self):
        json_data = json.loads(request.get_json())
        run_code(json_data["uuid"], json_data["code"], json_data["tests"], app)
        return jsonify({'success': 'OK'})


app = Flask(__name__)
api = Api(app)
api.add_resource(SolutionResource, "/api/solutions")

app.config['SECRET_KEY'] = 'yabrortus'

cnf_file = open("./config/testing.json")
cnf_data = json.loads(cnf_file.read())
cnf_file.close()

app.config['HOST'] = cnf_data["host"]
app.config['PORT'] = cnf_data["port"]
app.config['MAIN_SERVER_ADDRESS'] = cnf_data["main_server_address"]


if __name__ == '__main__':
    if not os.path.exists("./testing"):
        os.mkdir("./testing")
    app.run(port=app.config["PORT"], host=app.config["HOST"])
