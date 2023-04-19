import json
import os
import subprocess

import requests

import ProblemStatusTypes


def run_code(uuid: str, code: str, tests_json: str, app) -> None:
    try:
        os.mkdir(f"./testing/{uuid}")
        file = open(f"./testing/{uuid}/solution.py", "w")
        file.write(code)
        file.close()

        tests = json.loads(tests_json)
        for test in tests:
            result = subprocess.check_output(
                ["python3", f"./testing/{uuid}/solution.py"],
                timeout=1.0,
                stderr=subprocess.STDOUT,
                input=bytes(test[0], "utf-8")
            )
            result = result.decode("utf-8")

            if result == test[1]:
                continue

            elif result.startswith("Exception:"):

                os.remove(f"./testing/{uuid}/solution.py")
                os.rmdir(f"./testing/{uuid}")
                return

            else:
                requests.post(
                    f"http://{app.config['MAIN_SERVER_ADDRESS']}/api/solution_testing",
                    json=json.dumps(
                        {"uuid": uuid, "status": ProblemStatusTypes.WRONG, "msg": "Wrong answer!"}
                    )
                )

                os.remove(f"./testing/{uuid}/solution.py")
                os.rmdir(f"./testing/{uuid}")
                return

        requests.post(
            f"http://{app.config['MAIN_SERVER_ADDRESS']}/api/solution_testing",
            json=json.dumps(
                {"uuid": uuid, "status": ProblemStatusTypes.SUCCESS, "msg": "OK"}
            )
        )

    except subprocess.TimeoutExpired:
        requests.post(
            f"http://{app.config['MAIN_SERVER_ADDRESS']}/api/solution_testing",
            json=json.dumps(
                {"uuid": uuid, "status": ProblemStatusTypes.TIME_LIMIT, "msg": "Time limit error!"}
            )
        )

    except subprocess.CalledProcessError as e:
        output = "<p>" + e.output.decode().replace("\n", "<p>")
        if "SyntaxError" in output:
            requests.post(
                f"http://{app.config['MAIN_SERVER_ADDRESS']}/api/solution_testing",
                json=json.dumps(
                    {"uuid": uuid, "status": ProblemStatusTypes.SYNTAX_ERROR, "msg": "Syntax error:\n" + output}
                )
            )
        else:
            requests.post(
                f"http://{app.config['MAIN_SERVER_ADDRESS']}/api/solution_testing",
                json=json.dumps(
                    {"uuid": uuid, "status": ProblemStatusTypes.EXCEPTION, "msg": "Runtime error:\n" + output}
                )
            )

    os.remove(f"./testing/{uuid}/solution.py")
    os.rmdir(f"./testing/{uuid}")
