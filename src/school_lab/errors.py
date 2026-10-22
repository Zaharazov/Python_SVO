from enum import StrEnum

class ErrorCode(StrEnum):
    INVALID_JSON = "invalid_json"
    SCHEMA_ERROR = "schema_error"
    UNSUPPORTED_VERSION = "unsupported_version"
    CONFLICT = "conflict"

class SubmissionError(Exception):
    def __init__(self, code: ErrorCode, field: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code.value, "field": self.field, "message": self.message}