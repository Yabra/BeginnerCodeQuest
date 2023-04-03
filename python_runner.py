from enum import Enum
import subprocess
import traceback
import json
import os


class ReturnType(Enum):
    SUCCESS = 0
    WRONG = 1
    EXCEPTION = 2


def run_code(code: str, tests_json: str) -> tuple[ReturnType.EXCEPTION, str]:
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
            return ReturnType.EXCEPTION, result

        else:
            os.remove("./solution.py")
            os.remove("./input.txt")
            return ReturnType.WRONG

    os.remove("./solution.py")
    os.remove("./input.txt")
    return ReturnType.SUCCESS


print(
    run_code(
        "s = input()\nprint(f\"Hello, {s}!\")\n",
        json.dumps(
            [("Ярослав", "Hello, Ярослав!\n"), ("Влад", "Hello, Влад!\n"), ("Pavel", "Hello, Pavel!\n")]
        )
    )
)
