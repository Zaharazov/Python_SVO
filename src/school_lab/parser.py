import json

from pydantic import ValidationError

from .errors import ErrorCode, SubmissionError
from .models import Submission
from .schemas import SubmissionInput

def _reject_repeated_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SubmissionError(ErrorCode.INVALID_JSON, key, "Повтор ключа в JSON-объекте не допускается")
        result[key] = value
    return result

def _reject_constant(value: str) -> object:
    raise SubmissionError(ErrorCode.INVALID_JSON, "json", f"Нестандартное значение не допускается: {value}")

def decode_json(line: str) -> object:
    try:
        return json.loads(line, object_pairs_hook=_reject_repeated_keys, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise SubmissionError(ErrorCode.INVALID_JSON, "json", f"Ошибка JSON около столбца {exc.colno}") from exc

def _to_submission_error(exc: ValidationError) -> SubmissionError:
    first = exc.errors(include_url=False, include_context=False)[0]
    loc = first["loc"]
    message = first["msg"].removeprefix("Value error, ")
    field = ".".join(str(part) for part in loc) or "text/code"
    if loc == ("schema_version",) and first["type"] == "value_error":
        return SubmissionError(ErrorCode.UNSUPPORTED_VERSION, field, message)
    return SubmissionError(ErrorCode.SCHEMA_ERROR, field, message)


def parse_submission(raw: object) -> Submission:
    if not isinstance(raw, dict):
        raise SubmissionError(ErrorCode.SCHEMA_ERROR, "submission", "Ожидается JSON-объект")
    try:
        return SubmissionInput.model_validate(raw).to_domain()
    except ValidationError as exc:
        raise _to_submission_error(exc) from exc


def parse_submission_line(line: str) -> Submission:
    return parse_submission(decode_json(line))