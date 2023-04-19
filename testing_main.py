import json
import os
from multiprocessing import Pool

from flask import Flask, request

from testing import run_code

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yabrortus'
pool = Pool()


@app.route('/get_solution_data', methods=['POST'])
def get_solution_data():
    json_req = request.get_json()
    json_parsed = json.loads(json_req)
    run_code(json_parsed["uuid"], json_parsed["code"], json_parsed["tests"])

    return ""


if __name__ == '__main__':
    if not os.path.exists("./testing"):
        os.mkdir("./testing")
    app.run(port=5000, host='127.0.0.1')
