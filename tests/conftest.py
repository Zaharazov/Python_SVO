import copy
from pathlib import Path

import pytest

from school_lab.adapters import SubmissionAdapter
from school_lab.repositories import InMemorySubmissionRepository
from school_lab.services import SubmissionService

DATA_FILE = Path(__file__).parent.parent / "data" / "submissions.jsonl"

VALID_RAW: dict[str, object] = {
    "schema_version": 1,
    "submission_id": "sub-100",
    "student_id": "student-100",
    "assignment_id": "assignment-01",
    "submitted_at": "2026-09-01T10:00:00+03:00",
    "text": "Пояснение",
    "code": "print(1)\n",
    "template_id": "template-01",
    "ai_declaration": {"used": False, "tool": None, "purpose": None, "verified_by_student": True},
}

@pytest.fixture
def raw() -> dict[str, object]:
    return copy.deepcopy(VALID_RAW)

@pytest.fixture
def repository() -> InMemorySubmissionRepository:
    return InMemorySubmissionRepository()

@pytest.fixture
def service(repository: InMemorySubmissionRepository) -> SubmissionService:
    return SubmissionService(repository)

@pytest.fixture
def adapter(service: SubmissionService) -> SubmissionAdapter:
    return SubmissionAdapter(service)

@pytest.fixture
def data_file() -> Path:
    return DATA_FILE

@pytest.fixture
def public_lines(data_file: Path) -> list[str]:
    return data_file.read_text(encoding="utf-8").splitlines()