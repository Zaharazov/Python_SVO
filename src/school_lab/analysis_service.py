from .analyzers import validate_report
from .errors import AnalysisFailure
from .models import AnalysisContext, AnalysisReport
from .registry import AnalyzerRegistry
from .repositories import SubmissionRepository

class AnalysisService:
    def __init__(self, repository: SubmissionRepository, registry: AnalyzerRegistry) -> None:
        self.repository = repository
        self.registry = registry

    def run(self, submission_id: str, analyzer_name: str, context: AnalysisContext) -> AnalysisReport:
        value = self.repository.get(submission_id)
        if value is None:
            raise AnalysisFailure("Анализ возможен после приёма сдачи")
        if value.assignment_id != context.assignment.assignment_id:
            raise AnalysisFailure("Требуется контекст соответствующего задания")
        analyzer = self.registry.create(analyzer_name)
        report = analyzer.analyze(value, context)
        validate_report(report, value, context)
        if report.analyzer_id != analyzer.analyzer_id or report.analyzer_version != analyzer.analyzer_version:
            raise AnalysisFailure("Отчёт не соответствует вызванному анализатору")
        return report