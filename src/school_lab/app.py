from .registry import AnalyzerRegistry
from dataclasses import dataclass
from .analyzers import LengthAnalyzer, TemplateAnalyzer
from .analysis_service import AnalysisService
from .adapters import SubmissionAdapter
from .services import SubmissionService
from .repositories import InMemorySubmissionRepository

@dataclass
class DemoApplication:
    repository: InMemorySubmissionRepository
    submission_service: SubmissionService
    adapter: SubmissionAdapter
    analysis_service: AnalysisService

def build_application() -> DemoApplication:
    repository = InMemorySubmissionRepository()
    submission_service = SubmissionService(repository)
    registry = AnalyzerRegistry()
    registry.register("length", LengthAnalyzer)
    registry.register("template", TemplateAnalyzer)
    return DemoApplication(
        repository=repository,
        submission_service=submission_service,
        adapter=SubmissionAdapter(submission_service),
        analysis_service=AnalysisService(repository, registry),
    )