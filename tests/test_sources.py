import json
import copy
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from school_lab.errors import ErrorCode
from school_lab.sources import InMemorySource, JSONLSource, SourceRecord, SubmissionSource

def read_all(source: SubmissionSource) -> list[SourceRecord]:
    with source.open() as records:
        return list(records)

@pytest.fixture
def two_records(raw: dict[str, object]) -> list[dict[str, object]]:
    second = copy.deepcopy(raw)
    second["submission_id"] = "sub-101"
    second["text"] = "Вторая версия"
    return [raw, second]

@pytest.fixture
def write_jsonl(tmp_path: Path) -> Callable[[Sequence[str]], Path]:
    def _write(lines: Sequence[str]) -> Path:
        path = tmp_path / "submissions.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
    return _write

@pytest.fixture
def jsonl_source(
    write_jsonl: Callable[[Sequence[str]], Path], two_records: list[dict[str, object]]
) -> JSONLSource:
    return JSONLSource(write_jsonl([json.dumps(record, ensure_ascii=False) for record in two_records]))

@pytest.fixture(params=["memory", "jsonl"])
def source(
    request: pytest.FixtureRequest, two_records: list[dict[str, object]], jsonl_source: JSONLSource
) -> SubmissionSource:
    return InMemorySource(two_records) if request.param == "memory" else jsonl_source

def test_records_keep_order_and_line_numbers(
    source: SubmissionSource, two_records: list[dict[str, object]]
) -> None:
    records = read_all(source)
    assert [record.line_no for record in records] == [1, 2]
    assert [record.raw for record in records] == two_records
    assert all(record.error is None for record in records)

def test_changing_a_record_does_not_affect_the_source(
    source: SubmissionSource, two_records: list[dict[str, object]]
) -> None:
    with source.open() as records:
        first = next(records)
        assert isinstance(first.raw, dict)
        first.raw["student_id"] = "changed"
    assert read_all(source)[0].raw == two_records[0]

def test_in_memory_source_copies_its_input(two_records: list[dict[str, object]]) -> None:
    source = InMemorySource(two_records)
    two_records[0]["student_id"] = "changed"
    first = read_all(source)[0].raw
    assert isinstance(first, dict)
    assert first["student_id"] == "student-100"

def test_jsonl_broken_line_becomes_error_and_reading_continues(
    write_jsonl: Callable[[Sequence[str]], Path], two_records: list[dict[str, object]]
) -> None:
    lines = [json.dumps(two_records[0]), "{broken", json.dumps(two_records[1])]
    records = read_all(JSONLSource(write_jsonl(lines)))

    assert [record.line_no for record in records] == [1, 2, 3]
    assert records[1].raw is None
    assert records[1].error is not None
    assert records[1].error.code == ErrorCode.INVALID_JSON
    assert records[0].raw == two_records[0]
    assert records[2].raw == two_records[1]

def test_file_is_closed_after_normal_exit(jsonl_source: JSONLSource) -> None:
    assert jsonl_source.last_closed is None
    read_all(jsonl_source)
    assert jsonl_source.last_closed is True

def test_file_is_closed_after_early_exit(jsonl_source: JSONLSource) -> None:
    with jsonl_source.open() as records:
        next(records)
    assert jsonl_source.last_closed is True

def test_file_is_closed_after_error_inside_with(jsonl_source: JSONLSource) -> None:
    with pytest.raises(RuntimeError):
        with jsonl_source.open() as records:
            next(records)
            raise RuntimeError("ошибка при обработке записи")
    assert jsonl_source.last_closed is True