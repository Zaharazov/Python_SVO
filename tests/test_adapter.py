import copy
import json
from pathlib import Path

import pytest

from school_lab.adapters import SubmissionAdapter
from school_lab.errors import ErrorCode, SubmissionError
from school_lab.repositories import InMemorySubmissionRepository

def test_accept_payload_converts_dto_to_domain(
    adapter: SubmissionAdapter, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    before = copy.deepcopy(raw)
    result = adapter.accept_payload(raw)
    assert result.status == "accepted"
    assert result.submission.student_id == "student-100"
    assert repository.get("sub-100") is not None
    assert raw == before

def test_accept_payload_invalid_saves_nothing(
    adapter: SubmissionAdapter, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    raw["student_id"] = ""
    with pytest.raises(SubmissionError):
        adapter.accept_payload(raw)
    assert len(repository) == 0

def test_import_public_records(
    adapter: SubmissionAdapter, repository: InMemorySubmissionRepository, public_lines: list[str]
) -> None:
    report = adapter.import_lines(public_lines)
    assert len(report.accepted) == 12
    assert report.duplicate == []
    assert report.errors == []
    assert len(repository) == 12

def test_import_continues_after_bad_lines(
    adapter: SubmissionAdapter, repository: InMemorySubmissionRepository, public_lines: list[str]
) -> None:
    conflict = json.loads(public_lines[0])
    conflict["text"] = "другое"
    lines = [
        public_lines[0],                                   # 1 accepted
        "{broken",                                         # 2 invalid_json
        public_lines[0],                                   # 3 duplicate
        "",                                                # 4 пустая, пропускается
        json.dumps(conflict, ensure_ascii=False),          # 5 conflict
        json.dumps({"x": 1}),                              # 6 schema_error
        public_lines[1],                                   # 7 accepted
    ]

    report = adapter.import_lines(lines)

    assert report.accepted == ["sub-001", "sub-002"]
    assert report.duplicate == ["sub-001"]
    assert [(e.line, e.code) for e in report.errors] == [
        (2, ErrorCode.INVALID_JSON),
        (5, ErrorCode.CONFLICT),
        (6, ErrorCode.SCHEMA_ERROR),
    ]
    assert len(repository) == 2
    stored = repository.get("sub-001")
    assert stored is not None and stored.text != "другое"

def test_report_to_dict_is_json_serializable(adapter: SubmissionAdapter) -> None:
    report = adapter.import_lines(["{broken"])
    data = json.loads(json.dumps(report.to_dict(), ensure_ascii=False))
    assert data["errors"][0] == {
        "line": 1,
        "code": "invalid_json",
        "field": "json",
        "message": data["errors"][0]["message"],
    }

def test_import_file(adapter: SubmissionAdapter, data_file: Path) -> None:
    report = adapter.import_file(data_file)
    assert len(report.accepted) == 12 and report.errors == []

def test_import_file_with_broken_line(
    adapter: SubmissionAdapter, data_file: Path, tmp_path: Path
) -> None:
    good = data_file.read_text(encoding="utf-8").splitlines()[0]
    path = tmp_path / "mixed.jsonl"
    path.write_text(good + "\n{broken\n", encoding="utf-8")
    report = adapter.import_file(path)
    assert report.accepted == ["sub-001"]
    assert [e.line for e in report.errors] == [2]