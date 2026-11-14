from .parser import parse_submission
from .services import Acceptance, SubmissionService

class SubmissionAdapter:
    def __init__(self, service: SubmissionService) -> None:
        self._service = service

    def accept_payload(self, raw: object) -> Acceptance:
        return self._service.accept(parse_submission(raw))