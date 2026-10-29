import copy
import json

import pytest

from school_lab.errors import ErrorCode, SubmissionError
from school_lab.parser import parse_submission, parse_submission_line
from school_lab.models import Submission
from school_lab.schemas import SubmissionInput

MISSING = object()

INVALID_CASES = [
    ({"schema_version": True}, ErrorCode.SCHEMA_ERROR, "schema_version"),
    ({"schema_version": 2}, ErrorCode.UNSUPPORTED_VERSION, "schema_version"),
    ({"code": 123}, ErrorCode.SCHEMA_ERROR, "code"),
    ({"submitted_at": "2026-09-01T10:00:00"}, ErrorCode.SCHEMA_ERROR, "submitted_at"),
    ({"submitted_at": "вчера"}, ErrorCode.SCHEMA_ERROR, "submitted_at"),
    ({"student_id": "  "}, ErrorCode.SCHEMA_ERROR, "student_id"),
    ({"student_id": MISSING}, ErrorCode.SCHEMA_ERROR, "student_id"),
    ({"unknown": "value"}, ErrorCode.SCHEMA_ERROR, "unknown"),
    ({"text": " ", "code": "\n"}, ErrorCode.SCHEMA_ERROR, "text/code"),
    (
        {"ai_declaration": {"used": True, "tool": None, "purpose": None, "verified_by_student": False}},
        ErrorCode.SCHEMA_ERROR,
        "ai_declaration",
    ),
]

def test_valid_record_is_parsed(raw: dict[str, object]) -> None:
    submission = parse_submission(raw)
    assert submission.submission_id == "sub-100"
    assert submission.submitted_at == raw["submitted_at"]
    assert submission.ai_declaration.verified_by_student is True

def test_all_public_records_are_valid(public_lines: list[str]) -> None:
    assert len([parse_submission_line(line) for line in public_lines]) == 12

@pytest.mark.parametrize(("updates", "code", "field"), INVALID_CASES)
def test_invalid_record_gives_explainable_error(
    raw: dict[str, object], updates: dict[str, object], code: ErrorCode, field: str
) -> None:
    for key, value in updates.items():
        if value is MISSING:
            del raw[key]
        else:
            raw[key] = value
    before = copy.deepcopy(raw)

    with pytest.raises(SubmissionError) as info:
        parse_submission(raw)

    assert info.value.code == code
    assert info.value.field == field
    assert info.value.message
    assert raw == before

@pytest.mark.parametrize(
    "line",
    ["{broken", '{"student_id": "a", "student_id": "b"}', '{"score": NaN}'],
)
def test_broken_json_is_invalid_json(line: str) -> None:
    with pytest.raises(SubmissionError) as info:
        parse_submission_line(line)
    assert info.value.code == ErrorCode.INVALID_JSON

def test_json_array_is_schema_error() -> None:
    with pytest.raises(SubmissionError) as info:
        parse_submission_line(json.dumps([1, 2]))
    assert info.value.code == ErrorCode.SCHEMA_ERROR

def test_dto_converts_to_domain_object(raw: dict[str, object]) -> None:
    domain = SubmissionInput.model_validate(raw).to_domain()
    assert isinstance(domain, Submission)