# Руководство разработчика

## Современная конфигурация проекта

Проект использует современный стандарт `pyproject.toml` (PEP 518, PEP 621) вместо устаревших `setup.py` и `requirements.txt`.

### Структура pyproject.toml

```toml
[build-system]           # Система сборки
[project]               # Метаданные проекта
[project.optional-dependencies]  # Дополнительные зависимости
[project.scripts]       # Entry points для CLI
[tool.*]                # Настройки инструментов разработки
```

## Установка для разработки

```bash
# Клонирование репозитория
git clone <repository-url>
cd fpga-pipeline-generator

# Установка в режиме разработки со всеми зависимостями
pip install -e .[dev]
```

## Инструменты разработки

### Форматирование кода
```bash
# Автоформатирование с black
black fpga_pipeline_generator/

# Сортировка импортов с isort
isort fpga_pipeline_generator/
```

### Проверка качества кода
```bash
# Статическая проверка типов
mypy fpga_pipeline_generator/

# Линтер
flake8 fpga_pipeline_generator/
```

### Тестирование
```bash
# Запуск тестов
pytest

# Тесты с покрытием
pytest --cov=fpga_pipeline_generator

# Генерация HTML отчета о покрытии
pytest --cov=fpga_pipeline_generator --cov-report=html
```

## Управление зависимостями

### Основные зависимости
Указываются в секции `[project] dependencies`:
- `PyYAML>=6.0` - работа с YAML файлами
- `Jinja2>=3.0.0` - шаблонизация

### Дополнительные зависимости
```bash
# Установка с зависимостями для разработки
pip install -e .[dev]

# Установка с зависимостями для документации
pip install -e .[docs]
```

## Настройки инструментов

Все настройки инструментов разработки хранятся в `pyproject.toml`:

- **Black**: Форматирование кода (длина строки 100 символов)
- **isort**: Сортировка импортов (совместимо с black)
- **mypy**: Проверка типов (строгий режим)
- **pytest**: Тестирование
- **coverage**: Покрытие кода

## Создание релиза

```bash
# Обновление версии в pyproject.toml
# [project] version = "1.1.0"

# Создание дистрибутива
pip install build
python -m build

# Загрузка в PyPI (после настройки токенов)
pip install twine
twine upload dist/*
```

## Структура пакета

```
fpga_pipeline_generator/
├── __init__.py          # Точка входа пакета
├── __main__.py          # Запуск как модуль (-m)
├── main.py              # CLI интерфейс
├── core/                # Основная логика
│   ├── config_loader.py # Загрузка конфигураций
│   ├── parser.py        # Парсинг cfg.yaml
│   └── generator.py     # Генерация пайплайнов
├── templates/           # Jinja2 шаблоны
│   ├── pipeline.j2      # Шаблон пайплайна
│   └── job.j2          # Шаблон задач
├── config/              # Конфигурации по умолчанию
│   └── default.yaml     # Настройки стадий и правил
└── utils/               # Вспомогательные утилиты
    └── file_utils.py    # Работа с файлами
```

## Преимущества pyproject.toml

1. **Стандартизация**: Следует современным PEP стандартам
2. **Единый файл**: Вся конфигурация в одном месте
3. **Декларативность**: Четкое разделение метаданных и логики
4. **Инструментальная поддержка**: Лучшая интеграция с современными инструментами
5. **Расширяемость**: Легко добавлять настройки новых инструментов

## Миграция с setup.py

Основные изменения при переходе на `pyproject.toml`:

- ✅ Метаданные проекта в секции `[project]`
- ✅ Зависимости в `dependencies` и `optional-dependencies`
- ✅ Entry points в `[project.scripts]`
- ✅ Настройки инструментов в секциях `[tool.*]`
- ✅ Система сборки в `[build-system]`

## Совместимость

Проект поддерживает Python 3.8+ и совместим с:
- pip (современные версии)
- setuptools (как build backend)
- wheel (для создания колес)
- Все современные IDE и редакторы