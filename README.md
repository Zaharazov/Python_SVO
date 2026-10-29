# Python_SVO - Lab1 (Основной вариант Backend)

Разработайте основу системы онлайн-школы, которая принимает сдачи лабораторных, валидирует их 
и запускает заменяемые анализаторы. Работа длится недели 1–2 и включает два самостоятельных 
этапа. Итог станет основой следующих лабораторных. 

## Установка

Нужен Python 3.12 или новее.

### Windows (PowerShell):
 
```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```
 
### macOS / Linux:
 
```
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Запуск тестов
 
```
pytest
```
 
Ожидаемый результат: `31 passed`.

## Запуск импорта тестовых данных

Файл `data/submissions.jsonl` содержит 12 учебных сдач (одна JSON-запись в строке).
Из корня проекта:

```
python -c "from school_lab.adapters import SubmissionAdapter; from school_lab.repositories import InMemorySubmissionRepository; from school_lab.services import SubmissionService; print(SubmissionAdapter(SubmissionService(InMemorySubmissionRepository())).import_file('data/submissions.jsonl'))"
```

Ожидаемый результат: `ImportReport(accepted=['sub-001', ..., 'sub-012'], duplicate=[], errors=[])`.