# FPGA Pipeline Generator

Генератор динамических CI/CD пайплайнов для FPGA проектов на основе конфигурационных файлов.

<<<<<<< HEAD
## 🚀 Быстрый старт

### Автоматическая настройка (рекомендуется)

```bash
# Создает виртуальное окружение и запускает утилиту
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run
=======
### Доступные опции утилиты :

```bash
fpga-pipeline-gen --help
usage: fpga-pipeline-gen [-h] [-o OUTPUT] [-c CONFIG] [--stages STAGES] [--fpga-dir FPGA_DIR] [--dry-run] [--verbose] [--version]

FPGA Pipeline Generator - генерирует динамические CI/CD пайплайны для FPGA проектов

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Путь к выходному файлу (по умолчанию: generated_pipeline.yml)
  -c CONFIG, --config CONFIG
                        Путь к пользовательскому файлу конфигурации
  --stages STAGES       Список стадий через запятую (переопределяет FPGA_TARGET_ARTIFACT)
  --fpga-dir FPGA_DIR   Директория с FPGA сабмодулями (по умолчанию: fpga)
  --dry-run             Не сохранять файл, только вывести результат
  --verbose             Подробный вывод
  --version             show program's version number and exit

Примеры использования:
  # Базовое использование (с переменной окружения FPGA_TARGET_ARTIFACT)
  python -m fpga_pipeline_generator

  # Указание выходного файла
  python -m fpga_pipeline_generator -o my_pipeline.yml

  # Использование пользовательской конфигурации
  python -m fpga_pipeline_generator -c custom_config.yaml

  # Установка целевых артефактов через аргумент
  python -m fpga_pipeline_generator --stages elab,synth

Переменные окружения:
  FPGA_TARGET_ARTIFACT - список стадий через запятую (elab,synth,bitstream)
>>>>>>> YSDTSRE-710
```

### Ручная настройка

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
<<<<<<< HEAD
pip install pyyaml

# Запуск утилиты
export FPGA_TARGET_ARTIFACT=elab
python fpga_gen.py --dry-run
```

## 📋 Доступные скрипты

- **`run_fpga_gen.sh`** - Основной скрипт с корректным YAML форматированием

## 🔧 Использование

### Базовые команды

```bash
# Просмотр сгенерированного пайплайна
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run

# Сохранение в файл
export FPGA_TARGET_ARTIFACT=elab,synth
./run_fpga_gen.sh -o my_pipeline.yml

# Подробный вывод
./run_fpga_gen.sh --dry-run --verbose
=======
pip install -e .

# Запуск утилиты
export FPGA_TARGET_ARTIFACT=elab (задание тестовой переменной окружения)
fpga-pipeline-gen --dry-run
>>>>>>> YSDTSRE-710
```

### Переменные окружения

- `FPGA_TARGET_ARTIFACT` - список стадий через запятую (elab,synth,bitstream)

<<<<<<< HEAD
## 📁 Структура проекта

```
fpga/
├── test_fpga/
│   └── cfg.yaml          # Конфигурация сабмодуля
fpga_pipeline_generator/
├── config/
│   └── default.yaml      # Конфигурация по умолчанию
├── templates/
│   ├── pipeline.j2       # Шаблон пайплайна (не используется)
│   └── job.j2           # Шаблон задачи (не используется)
└── core/
    ├── generator.py      # Основная логика
    └── parser.py         # Парсер конфигураций
```

## 📝 Формат конфигурации

### cfg.yaml (в сабмодулях)
=======

## 📝 Формат конфигурации

### cfg.yaml (в сабмодулях) Используется только FPGA_TARGET_ARTIFACT=elab
>>>>>>> YSDTSRE-710

```yaml
elab:
  - target: "lsio_au_elab"
    variables:
      FPGA_BOARD_TYPE: "HTG960"
      FPGA_DEVICE: "xczu7ev"
    options: []

synth:
  - target: "lsio_au_synth"
    variables:
      FPGA_BOARD_TYPE: "HTG960"
    options: ["--optimize"]
```

<<<<<<< HEAD
### Генерируемый YAML
=======
### Пример сгенерированного YAML с переменной окружения FPGA_TARGET_ARTIFACT=elab
>>>>>>> YSDTSRE-710

```yaml
# Generated FPGA Pipeline
stages:
  - elab
<<<<<<< HEAD
  - synth
=======
>>>>>>> YSDTSRE-710

elab_lsio_au_elab_test_fpga:
  stage: elab
  tags: ["devops-elab"]
  script:
    - "echo elab VAR='FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev' TARGET='lsio_au_elab'"
    - "echo 'Executing: make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev'"
<<<<<<< HEAD
    - "export FPGA_BOARD_TYPE=HTG960"
    - "export FPGA_DEVICE=xczu7ev"
    - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev"
  rules:
    - if: "$CI_MERGE_REQUEST_ID"
  variables:
    FPGA_STAGE: "elab"
    FPGA_TARGET: "lsio_au_elab"
    FPGA_SUBMODULE: "test_fpga"
    FPGA_WORKSPACE: "/workspace"
    MAKEFILE_PATH: "Makefile"
    FPGA_BOARD_TYPE: "HTG960"
    FPGA_DEVICE: "xczu7ev"
```

## 🛠️ Устранение неполадок

### Проблема: "python3-venv не установлен"
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

### Проблема: "PyYAML не установлен"
```bash
source venv/bin/activate
pip install pyyaml
```

### Проблема: Неправильное форматирование YAML
Утилита использует встроенную генерацию с корректным YAML форматированием.

## 📚 Дополнительная документация

- [VENV_USAGE.md](VENV_USAGE.md) - Подробное руководство по использованию через venv
- [DEVELOPMENT.md](DEVELOPMENT.md) - Руководство для разработчиков

## 🔄 Последние изменения

- ✅ Исправлено форматирование YAML
- ✅ Добавлена поддержка переменных из cfg.yaml
- ✅ Создан скрипт для автоматической настройки venv
- ✅ Улучшена встроенная генерация
- ✅ Добавлена поддержка опций в конфигурации
- ✅ Отключен Jinja2 для стабильной работы
=======
    - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev"
  rules:
    - if: "$CI_MERGE_REQUEST_ID"
```



>>>>>>> YSDTSRE-710
