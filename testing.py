import subprocess
import traceback
import json
import os
import requests
import ProblemStatusTypes


def run_code(uuid: str, code: str, tests_json: str) -> None:
    code = "import traceback\n" \
           "__input_file = open(\"input.txt\")\n" \
           "def input(s=\"\"):\n" \
           "    print(s, end=\"\")\n" \
           "    return __input_file.readline().rstrip(\"\\n\")\n" \
           "try:\n" + \
           "\n".join(["    " + s for s in code.split("\n")]) + "\n" + \
           "    __input_file.close()\n" \
           "except Exception as e:\n" \
           "    print(\"Exception: \" + e.__class__.__name__ + \"\\n\" +" \
           " ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))\n"

    file = open("./solution.py", "w")
    file.write(code)
    file.close()

    tests = json.loads(tests_json)
    for test in tests:
        input_file = open("./input.txt", "w")
        input_file.write(test[0])
        input_file.close()

        result = subprocess.check_output(['python3', './solution.py']).decode("utf-8")
        if result == test[1]:
            continue

        elif result.startswith("Exception:"):
            requests.post(
                "http://127.0.0.1:8080/api/solution_testing",
                json=json.dumps(
                    {"uuid": uuid, "status": ProblemStatusTypes.EXCEPTION, "msg": result}
                )
            )

            os.remove("./solution.py")
            os.remove("./input.txt")
            return

        else:
            requests.post(
                "http://127.0.0.1:8080/api/solution_testing",
                json=json.dumps(
                    {"uuid": uuid, "status": ProblemStatusTypes.WRONG, "msg": "Wrong answer!"}
                )
            )

            os.remove("./solution.py")
            os.remove("./input.txt")
            return

    requests.post(
        "http://127.0.0.1:8080/api/solution_testing",
        json=json.dumps(
            {"uuid": uuid, "status": ProblemStatusTypes.SUCCESS, "msg": "OK"}
        )
    )

    os.remove("./solution.py")
    os.remove("./input.txt")
