import dataclasses
from collections.abc import Iterable
from pathlib import Path

from .errors import SubmissionError
from .parser import parse_submission, decode_json
from .services import Acceptance, SubmissionService

@dataclasses.dataclass(frozen=True, slots=True)
class LineError:
    line: int
    code: str
    field: str
    message: str

@dataclasses.dataclass(slots=True)
class ImportReport:
    accepted: list[str] = dataclasses.field(default_factory=list)
    duplicate: list[str] = dataclasses.field(default_factory=list)
    errors: list[LineError] = dataclasses.field(default_factory=list)

class SubmissionAdapter:
    def __init__(self, service: SubmissionService) -> None:
        self._service = service

    def accept_payload(self, raw: object) -> Acceptance:
        return self._service.accept(parse_submission(raw))

    def import_lines(self, lines: Iterable[str]) -> ImportReport:
        report = ImportReport()
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                result = self.accept_payload(decode_json(line))
            except SubmissionError as exc:
                report.errors.append(LineError(number, exc.code.value, exc.field, exc.message))
                continue
            target = report.accepted if result.status == "accepted" else report.duplicate
            target.append(result.submission.submission_id)
        return report

    def import_file(self, path: Path | str) -> ImportReport:
        with open(path, encoding="utf-8") as file:
            return self.import_lines(file)