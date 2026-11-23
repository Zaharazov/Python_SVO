import copy

import pytest

from school_lab.analyzers import Analyzer, LengthAnalyzer, TemplateAnalyzer, template_ranges
from school_lab.hashing import submission_hash
from school_lab.models import AnalysisContext, Submission
from school_lab.parser import parse_submission


@pytest.fixture
def submission(raw: dict[str, object]) -> Submission:
    raw["text"] = "Первая строка\n\nТретья строка\n"
    raw["code"] = "from typing import Iterable\n\ndef solve(values: Iterable[int]) -> int:\n    return 0\n"
    return parse_submission(raw)


@pytest.fixture(params=[LengthAnalyzer, TemplateAnalyzer])
def analyzer(request: pytest.FixtureRequest) -> Analyzer:
    analyzer: Analyzer = request.param()
    return analyzer

def test_report_matches_submission_and_analyzer(
    analyzer: Analyzer, submission: Submission, context: AnalysisContext
) -> None:
    report = analyzer.analyze(submission, context)
    assert report.submission_id == submission.submission_id
    assert report.submission_hash == submission_hash(submission)
    assert report.analyzer_id == analyzer.analyzer_id
    assert report.analyzer_version == analyzer.analyzer_version
    assert report.findings

def test_evidence_points_to_existing_lines(
    analyzer: Analyzer, submission: Submission, context: AnalysisContext
) -> None:
    report = analyzer.analyze(submission, context)
    for finding in report.findings:
        for evidence in finding.evidence:
            lines = getattr(submission, evidence.field).splitlines()
            assert 1 <= evidence.start_line <= evidence.end_line <= len(lines)

def test_analysis_does_not_change_submission(
    analyzer: Analyzer, submission: Submission, context: AnalysisContext
) -> None:
    snapshot = copy.deepcopy(submission)
    analyzer.analyze(submission, context)
    assert submission == snapshot

def test_length_counts_nonempty_lines(submission: Submission, context: AnalysisContext) -> None:
    finding = LengthAnalyzer().analyze(submission, context).findings[0]
    assert finding.kind == "rubric_feedback"
    assert finding.score is None
    assert [(e.field, e.start_line) for e in finding.evidence] == [
        ("text", 1),
        ("text", 3),
        ("code", 1),
        ("code", 3),
        ("code", 4),
    ]
    assert "text=2" in finding.explanation and "code=3" in finding.explanation

@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("x\n\na\nb\n", ((3, 4),)),
        ("  a\nb\n", ()),
    ],
)
def test_template_ranges(code: str, expected: tuple[tuple[int, int], ...]) -> None:
    assert template_ranges(code, "a\nb\n") == expected


def test_template_match_is_reported_as_allowed(submission: Submission, context: AnalysisContext) -> None:
    finding = TemplateAnalyzer().analyze(submission, context).findings[0]
    assert finding.kind == "similarity"
    assert [(e.field, e.start_line, e.end_line) for e in finding.evidence] == [("code", 1, 1)]
    assert "допустимое совпадение" in finding.explanation