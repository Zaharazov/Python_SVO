from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .models import AIDeclaration, Submission

SUPPORTED_SCHEMA_VERSION = 1

_STRICT = ConfigDict(strict=True, extra="forbid", frozen=True)

class DeclarationInput(BaseModel):
    model_config = _STRICT

    used: bool
    tool: str | None
    purpose: str | None
    verified_by_student: bool

    @field_validator("tool", "purpose")
    @classmethod
    def nonempty_or_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Допускается непустая строка либо null")
        return value

    @model_validator(mode="after")
    def used_requires_details(self) -> Self:
        if self.used and (self.tool is None or self.purpose is None):
            raise ValueError("При used=true обязательны tool и purpose")
        return self

class SubmissionInput(BaseModel):
    model_config = _STRICT

    schema_version: int
    submission_id: str
    student_id: str
    assignment_id: str
    submitted_at: str
    text: str
    code: str
    template_id: str | None
    ai_declaration: DeclarationInput

    @field_validator("schema_version")
    @classmethod
    def supported_version(cls, value: int) -> int:
        if value != SUPPORTED_SCHEMA_VERSION:
            raise ValueError(f"Поддерживается версия схемы {SUPPORTED_SCHEMA_VERSION}")
        return value

    @field_validator("submission_id", "student_id", "assignment_id", "template_id")
    @classmethod
    def identifier_nonempty(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Требуется непустой идентификатор")
        return value

    @field_validator("submitted_at")
    @classmethod
    def timestamp_with_timezone(cls, value: str) -> str:
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Ожидается дата и время в формате ISO 8601") from exc
        if parsed.utcoffset() is None:
            raise ValueError("Часовой пояс обязателен")
        return value

    @model_validator(mode="after")
    def text_or_code_present(self) -> Self:
        if not self.text.strip() and not self.code.strip():
            raise ValueError("Поле text или code должно быть непустым")
        return self

    def to_domain(self) -> Submission:
        declaration = AIDeclaration(
            used=self.ai_declaration.used,
            tool=self.ai_declaration.tool,
            purpose=self.ai_declaration.purpose,
            verified_by_student=self.ai_declaration.verified_by_student,
        )
        return Submission(
            schema_version=self.schema_version,
            submission_id=self.submission_id,
            student_id=self.student_id,
            assignment_id=self.assignment_id,
            submitted_at=self.submitted_at,
            text=self.text,
            code=self.code,
            template_id=self.template_id,
            ai_declaration=declaration,
        )