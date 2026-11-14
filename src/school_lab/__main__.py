from pathlib import Path

from .app import build_application
from .importer import import_source
from .models import AnalysisContext
from .sources import JSONLSource, load_assignment


def main() -> None:
    data_dir = Path("data")
    app = build_application()
    context = AnalysisContext(load_assignment(data_dir / "assignments.json"))

    summary = import_source(JSONLSource(data_dir / "submissions.jsonl"), app.adapter)
    print(f"Принято: {len(summary.accepted)}, дубликатов: {len(summary.duplicate)}, ошибок: {len(summary.errors)}")

    for submission_id in summary.accepted:
        for name in ("length", "template"):
            report = app.analysis_service.run(submission_id, name, context)
            print(f"{submission_id} [{report.analyzer_id}] {report.findings[0].explanation}")


if __name__ == "__main__":
    main()