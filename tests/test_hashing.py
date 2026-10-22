import pytest

from school_lab.hashing import canonical_json, stable_hash, submission_hash
from school_lab.parser import parse_submission

def test_hash_does_not_depend_on_key_order() -> None:
    assert stable_hash({"a": 1, "b": 2}) == stable_hash({"b": 2, "a": 1})

def test_hash_changes_with_content(raw: dict[str, object]) -> None:
    first = parse_submission(raw)
    raw["text"] = "Другой текст"
    second = parse_submission(raw)
    assert submission_hash(first) != submission_hash(second)

def test_nan_is_rejected() -> None:
    with pytest.raises(ValueError):
        canonical_json({"value": float("nan")})