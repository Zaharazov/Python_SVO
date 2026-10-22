from dataclasses import dataclass
from typing import Literal

from .errors import ErrorCode, SubmissionError
from .hashing import submission_hash
from .models import Submission
from .repositories import SubmissionRepository


@dataclass(frozen=True, slots=True)
class Acceptance:
    status: Literal["accepted", "duplicate"]
    submission: Submission
    content_hash: str

class SubmissionService:
    def __init__(self, repository: SubmissionRepository) -> None:
        self._repository = repository

    def accept(self, submission: Submission) -> Acceptance:
        digest = submission_hash(submission)
        previous = self._repository.get(submission.submission_id)
        if previous is not None:
            if submission_hash(previous) != digest:
                raise SubmissionError(
                    ErrorCode.CONFLICT, "submission_id", "Для новой версии требуется новый ID"
                )
            return Acceptance("duplicate", previous, digest)
        self._repository.add(submission)
        return Acceptance("accepted", submission, digest)