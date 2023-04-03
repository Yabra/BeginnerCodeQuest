from enum import Enum
import traceback


class ReturnType(Enum):
    SUCCESS = 0
    EXCEPTION = 1


def run_code(code: str) -> tuple[ReturnType.EXCEPTION, str]:
    try:
        exec(code)
        return ReturnType.SUCCESS
    except Exception as e:
        return ReturnType.EXCEPTION, "Exception: " + e.__class__.__name__ + "\n" + ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))


print(run_code("print(\"Hello World\")\nEXCERTION!!!!!"))
