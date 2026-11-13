from .adapters import SubmissionAdapter
from .errors import SubmissionError
from .sources import SubmissionSource
from dataclasses import dataclass, field

@dataclass
class ImportSummary:
    accepted: list[str] = field(default_factory=list)
    duplicate: list[str] = field(default_factory=list)
    errors: list[dict[str, object]] = field(default_factory=list)

def _error_entry(line_no: int, error: SubmissionError) -> dict[str, object]:
    return {"line_no": line_no, "code": error.code.value, "field": error.field, "message": error.message}

def import_source(source: SubmissionSource, adapter: SubmissionAdapter) -> ImportSummary:
    summary = ImportSummary()
    with source.open() as records:
        for record in records:
            if record.error is not None:
                summary.errors.append(_error_entry(record.line_no, record.error))
                continue
            try:
                result = adapter.accept_payload(record.raw)
            except SubmissionError as exc:
                summary.errors.append(_error_entry(record.line_no, exc))
            else:
                target = summary.accepted if result.status == "accepted" else summary.duplicate
                target.append(result.submission.submission_id)
    return summary