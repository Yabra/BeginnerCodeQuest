import json
import os
from multiprocessing import Pool

from flask import Flask, request

from testing import run_code

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yabrortus'

cnf_file = open("./config/testing.json")
cnf_data = json.loads(cnf_file.read())
cnf_file.close()

app.config['PORT'] = cnf_data["port"]
app.config['MAIN_SERVER_ADDRESS'] = cnf_data["main_server_address"]

pool = Pool()


@app.route('/get_solution_data', methods=['POST'])
def get_solution_data():
    json_req = request.get_json()
    json_parsed = json.loads(json_req)
    run_code(json_parsed["uuid"], json_parsed["code"], json_parsed["tests"], app)

    return ""


if __name__ == '__main__':
    if not os.path.exists("./testing"):
        os.mkdir("./testing")
    app.run(port=app.config["PORT"], host='127.0.0.1')
