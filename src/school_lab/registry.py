from collections.abc import Callable
from .analyzers import Analyzer
from .errors import AnalysisFailure

class AnalyzerRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], Analyzer]] = {}

    def register(self, name: str, factory: Callable[[], Analyzer]) -> None:
        if not name.strip() or name in self._factories:
            raise AnalysisFailure("Требуется непустое уникальное имя анализатора")
        self._factories[name] = factory

    def create(self, name: str) -> Analyzer:
        try:
            factory = self._factories[name]
        except KeyError as exc:
            raise AnalysisFailure(f"Неизвестный анализатор: {name}") from exc
        analyzer = factory()
        if analyzer.analyzer_id != name:
            raise AnalysisFailure("Имя регистрации не совпадает с analyzer_id")
        return analyzer