import dataclasses

import pytest

from school_lab.errors import ErrorCode, SubmissionError
from school_lab.parser import parse_submission
from school_lab.repositories import InMemorySubmissionRepository
from school_lab.services import SubmissionService


def test_new_submission_is_accepted(
    service: SubmissionService, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    submission = parse_submission(raw)
    result = service.accept(submission)
    assert result.status == "accepted"
    assert repository.get("sub-100") == submission
    assert len(repository) == 1

def test_duplicate_does_not_increase_count(
    service: SubmissionService, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    first = service.accept(parse_submission(raw))
    second = service.accept(parse_submission(raw))
    assert second.status == "duplicate"
    assert second.submission == first.submission
    assert second.content_hash == first.content_hash
    assert len(repository) == 1

def test_conflict_keeps_original(
    service: SubmissionService, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    original = parse_submission(raw)
    service.accept(original)
    raw["text"] = "Изменённая работа"

    with pytest.raises(SubmissionError) as info:
        service.accept(parse_submission(raw))

    assert info.value.code == ErrorCode.CONFLICT
    assert info.value.field == "submission_id"
    assert repository.get("sub-100") == original
    assert len(repository) == 1

def test_new_version_with_new_id_is_accepted(
    service: SubmissionService, repository: InMemorySubmissionRepository, raw: dict[str, object]
) -> None:
    service.accept(parse_submission(raw))
    raw["submission_id"] = "sub-101"
    raw["text"] = "Вторая версия"
    assert service.accept(parse_submission(raw)).status == "accepted"
    assert len(repository) == 2

def test_stored_submission_is_frozen(
    service: SubmissionService, raw: dict[str, object]
) -> None:
    stored = service.accept(parse_submission(raw)).submission
    with pytest.raises(dataclasses.FrozenInstanceError):
        stored.student_id = "other"