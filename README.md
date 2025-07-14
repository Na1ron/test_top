# FPGA Pipeline Generator

Утилита для автоматической генерации динамических пайплайнов на основе конфигурационных файлов cfg.yaml из сабмодулей FPGA.

## Описание

Утилита парсит файлы `cfg.yaml` из всех сабмодулей в папке `fpga` и создает YAML конфигурацию для динамического пайплайна. Генерация происходит на основе переменной окружения `FPGA_TARGET_ARTIFACT`, которая определяет, какие стадии (elab, synth, bitstream) должны быть включены в пайплайн.

## Установка

### Установка как пакет (рекомендуется)
```bash
# Обычная установка
pip install .

# Установка в режиме разработки
pip install -e .

# Установка с дополнительными зависимостями для разработки
pip install -e .[dev]

# Установка с зависимостями для документации
pip install -e .[docs]
```

### Использование без установки
```bash
# Запуск как модуль Python
python -m fpga_pipeline_generator

# Или через упрощенный CLI
./fpga_gen.py
```

### Для разработчиков
```bash
# Клонирование и установка в режиме разработки
git clone <repository-url>
cd fpga-pipeline-generator
pip install -e .[dev]

# Запуск тестов
pytest

# Форматирование кода
black .
isort .

# Проверка типов
mypy fpga_pipeline_generator
```

## Использование

### 1. Установка переменной окружения

Установите переменную `FPGA_TARGET_ARTIFACT` со списком нужных стадий через запятую:

```bash
# Только синтез
export FPGA_TARGET_ARTIFACT=synth

# Синтез и elaboration
export FPGA_TARGET_ARTIFACT=synth,elab

# Все стадии
export FPGA_TARGET_ARTIFACT=elab,synth,bitstream
```

### 2. Запуск утилиты

```bash
# Базовое использование
python -m fpga_pipeline_generator
# или
./fpga_gen.py

# Генерация в указанный файл
python -m fpga_pipeline_generator -o my_pipeline.yml

# Установка стадий через аргумент (переопределяет переменную окружения)
python -m fpga_pipeline_generator --stages elab,synth -o custom_pipeline.yml

# Просмотр результата без сохранения
python -m fpga_pipeline_generator --dry-run

# Подробный вывод для отладки
python -m fpga_pipeline_generator --verbose

# Использование пользовательской конфигурации
python -m fpga_pipeline_generator -c my_config.yaml
```

### 3. Справка по командам

```bash
python -m fpga_pipeline_generator --help
```

## Формат cfg.yaml

Утилита ожидает файлы `cfg.yaml` в следующем формате:

```yaml
elab:
  - target: lsio_au_elab
    vars: [FPGA_BOARD_TYPE=HTG960]

synth:
  - target: lsio_au
  - target: lsio_au_2
    vars: [FPGA_BOARD_TYPE=VCU118, USE_ORIG_MEM=1]
    options: [--write-netlist, --disable-reports]

bitstream:
  - target: lsio_au_cosim
    vars: [FPGA_BOARD_TYPE=HTG960]
    options: [--vivado-ver=2021.1]
```

### Поля конфигурации:

- **target** (обязательное) - название цели для сборки
- **vars** (необязательное) - список переменных в формате `VARIABLE=VALUE`
- **options** (необязательное) - список опций командной строки

## Команда echo с распаршенными данными

Каждая сгенерированная задача содержит специальную команду `echo`, которая выводит все распаршенные данные из cfg.yaml:

### Формат команды:
```bash
echo {stage_name} [VAR='переменные'] [OPTIONS='опции'] TARGET='цель'
```

### Примеры:

**Минимальная конфигурация** (только target):
```yaml
elab:
  - target: simple_target
```
Результат: `echo elab TARGET='simple_target'`

**С переменными** (target + vars):
```yaml
synth:
  - target: board_target
    vars: [BOARD=NEXYS, MODE=DEBUG]
```
Результат: `echo synth VAR='BOARD=NEXYS MODE=DEBUG' TARGET='board_target'`

**С опциями** (target + options):
```yaml
bitstream:
  - target: fast_target
    options: [--fast, --verbose]
```
Результат: `echo bitstream OPTIONS='--fast --verbose' TARGET='fast_target'`

**Полная конфигурация** (target + vars + options):
```yaml
synth:
  - target: full_target
    vars: [TOOL=VIVADO, VERSION=2023.1]
    options: [--parallel, --optimize]
```
Результат: `echo synth VAR='TOOL=VIVADO VERSION=2023.1' OPTIONS='--parallel --optimize' TARGET='full_target'`

### Правила формирования:
- Если `vars` отсутствует → часть `VAR='...'` не добавляется
- Если `options` отсутствует → часть `OPTIONS='...'` не добавляется  
- `TARGET='...'` присутствует всегда
- Порядок: `stage_name` → `VAR` → `OPTIONS` → `TARGET`

## Теги раннеров (Runner Tags)

Утилита автоматически назначает теги раннеров в зависимости от стадии FPGA пайплайна:

### Логика назначения тегов:

| Стадия | Тег раннера | Описание |
|--------|-------------|----------|
| `elab` | `devops-elab` | Раннеры для elaboration задач |
| `synth` | `devops-synth` | Раннеры для synthesis задач |
| `bitstream` | `devops-synth` | Раннеры для bitstream задач (используют тот же пул что и synth) |

### Примеры:

**Elaboration задача:**
```yaml
elab_target_name_submodule:
  stage: elab
  tags: ["devops-elab"]  # ← Раннер для elab
  # ... остальная конфигурация
```

**Synthesis задача:**
```yaml
synth_target_name_submodule:
  stage: synth
  tags: ["devops-synth"]  # ← Раннер для synth
  # ... остальная конфигурация
```

**Bitstream задача:**
```yaml
bitstream_target_name_submodule:
  stage: bitstream
  tags: ["devops-synth"]  # ← Тот же раннер что и для synth
  # ... остальная конфигурация
```

### Обоснование:
- **`elab`** использует отдельные раннеры, так как требует меньше ресурсов
- **`synth` и `bitstream`** используют общие мощные раннеры, так как обе стадии ресурсоемкие

## Структура проекта

```
.
├── fpga/
│   ├── submodule1/
│   │   └── cfg.yaml
│   ├── submodule2/
│   │   └── cfg.yaml
│   └── ...
├── fpga_pipeline_generator/         # Основной пакет
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                      # Точка входа
│   ├── core/                        # Основная логика
│   │   ├── config_loader.py
│   │   ├── parser.py
│   │   └── generator.py
│   ├── templates/                   # Jinja2 шаблоны
│   │   ├── pipeline.j2
│   │   └── job.j2
│   ├── config/                      # Конфигурации
│   │   └── default.yaml
│   └── utils/                       # Утилиты
│       └── file_utils.py
├── fpga_gen.py                      # Упрощенный CLI
├── pyproject.toml                   # Современная конфигурация проекта
├── LICENSE                          # Лицензия MIT
└── README.md
```

## Пример сгенерированного пайплайна

При `FPGA_TARGET_ARTIFACT=synth,elab` и наличии cfg.yaml в сабмодуле `test_fpga`:

```yaml
stages:
  - synth
  - elab
variables:
  FPGA_TARGET_ARTIFACT: synth,elab

elab_lsio_au_elab_test_fpga:
  stage: elab
  tags: ["devops-elab"]
  script:
    - "echo elab VAR='FPGA_BOARD_TYPE=HTG960' TARGET='lsio_au_elab'"
    - "echo 'Executing: make -f Makefile elab FPGA_BOARD_TYPE=HTG960'"
    - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960"
  rules:
    - if: "$CI_MERGE_REQUEST_ID"

synth_lsio_au_test_fpga:
  stage: synth
  tags: ["devops-synth"]
  script:
    - "echo synth TARGET='lsio_au'"
    - "echo 'Executing: make -f Makefile synth '"
    - "make -f Makefile synth "
  rules:
    - if: "$CI_MERGE_REQUEST_ID"

synth_lsio_au_2_test_fpga:
  stage: synth
  tags: ["devops-synth"]
  script:
    - "echo synth VAR='FPGA_BOARD_TYPE=VCU118 USE_ORIG_MEM=1' OPTIONS='--write-netlist --disable-reports' TARGET='lsio_au_2'"
    - "echo 'Executing: make -f Makefile synth FPGA_BOARD_TYPE=VCU118 USE_ORIG_MEM=1 --write-netlist --disable-reports'"
    - "make -f Makefile synth FPGA_BOARD_TYPE=VCU118 USE_ORIG_MEM=1 --write-netlist --disable-reports"
  rules:
    - if: "$CI_MERGE_REQUEST_ID"
```

## Особенности

1. **Современный стандарт**: Использует `pyproject.toml` вместо устаревших `setup.py` и `requirements.txt`
2. **Шаблонизация с Jinja2**: Поддержка Jinja2 шаблонов для гибкой настройки генерации (с fallback режимом)
3. **Модульная архитектура**: Полноценный Python пакет с разделением ответственности
4. **Конфигурируемость**: Настройка через YAML конфигурации с возможностью переопределения
5. **CI/CD готовность**: Генерация включает `tags`, `rules`, и корректные `make` команды
6. **Фильтрация по переменной окружения**: Утилита создает только те стадии, которые указаны в `FPGA_TARGET_ARTIFACT`
7. **Поддержка множественных сабмодулей**: Автоматически обнаруживает все сабмодули в папке `fpga`
8. **Наследование переменных**: Переменные из секции `vars` добавляются в конфигурацию задач
9. **Поддержка опций**: Опции из секции `options` передаются в переменную `FPGA_OPTIONS`
10. **Уникальные имена задач**: Имена формируются как `{stage}_{target}_{submodule}`
11. **CLI интерфейс**: Богатый интерфейс командной строки с различными опциями

## Отладка

Для отладки установите переменную окружения с выводом отладочной информации:

```bash
export FPGA_TARGET_ARTIFACT=synth,elab
python generate_fpga_pipeline.py
```

Утилита выведет информацию о найденных сабмодулях и созданных задачах.