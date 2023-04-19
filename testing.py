import json
import os
import subprocess

import requests

import ProblemStatusTypes


def run_code(uuid: str, code: str, tests_json: str) -> None:
    try:
        code = "import traceback\n" \
               "import argparse\n" \
               "parser = argparse.ArgumentParser()\n" \
               "parser.add_argument('input_file_path', type=str)\n" \
               "args = parser.parse_args()\n" \
               "__input_file = open(args.input_file_path)\n" \
               "def input(s=\"\"):\n" \
               "    print(s, end=\"\")\n" \
               "    return __input_file.readline().rstrip(\"\\n\")\n" \
               "try:\n" + \
               "\n".join(["    " + s for s in code.split("\n")]) + "\n" + \
               "    __input_file.close()\n" \
               "except Exception as e:\n" \
               "    print(\"Exception: \" + e.__class__.__name__ + \"\\n\" +" \
               " ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))\n"

        os.mkdir(f"./testing/{uuid}")
        file = open(f"./testing/{uuid}/solution.py", "w")
        file.write(code)
        file.close()

        tests = json.loads(tests_json)
        for test in tests:
            input_file = open(f"./testing/{uuid}/input.txt", "w")
            input_file.write(test[0])
            input_file.close()
            result = subprocess.check_output(
                ["python3", f"./testing/{uuid}/solution.py", f"./testing/{uuid}/input.txt"],
                timeout=1.0,
                stderr=subprocess.STDOUT
            )
            result = result.decode("utf-8")

            if result == test[1]:
                continue

            elif result.startswith("Exception:"):
                requests.post(
                    "http://127.0.0.1:8080/api/solution_testing",
                    json=json.dumps(
                        {"uuid": uuid, "status": ProblemStatusTypes.EXCEPTION, "msg": result}
                    )
                )

                os.remove(f"./testing/{uuid}/solution.py")
                os.remove(f"./testing/{uuid}/input.txt")
                os.rmdir(f"./testing/{uuid}")
                return

            else:
                requests.post(
                    "http://127.0.0.1:8080/api/solution_testing",
                    json=json.dumps(
                        {"uuid": uuid, "status": ProblemStatusTypes.WRONG, "msg": "Wrong answer!"}
                    )
                )

                os.remove(f"./testing/{uuid}/solution.py")
                os.remove(f"./testing/{uuid}/input.txt")
                os.rmdir(f"./testing/{uuid}")
                return

        requests.post(
            "http://127.0.0.1:8080/api/solution_testing",
            json=json.dumps(
                {"uuid": uuid, "status": ProblemStatusTypes.SUCCESS, "msg": "OK"}
            )
        )

    except subprocess.TimeoutExpired:
        requests.post(
            "http://127.0.0.1:8080/api/solution_testing",
            json=json.dumps(
                {"uuid": uuid, "status": ProblemStatusTypes.TIME_LIMIT, "msg": "Time limit error!"}
            )
        )

    except subprocess.CalledProcessError as e:
        requests.post(
            "http://127.0.0.1:8080/api/solution_testing",
            json=json.dumps(
                {"uuid": uuid, "status": ProblemStatusTypes.SYNTAX_ERROR, "msg": "Syntax error:\n" + e.output.decode()}
            )
        )

    os.remove(f"./testing/{uuid}/solution.py")
    os.remove(f"./testing/{uuid}/input.txt")
    os.rmdir(f"./testing/{uuid}")
