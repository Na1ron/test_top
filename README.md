# FPGA Pipeline Generator

Генератор динамических CI/CD пайплайнов для FPGA проектов на основе конфигурационных файлов.

## 🚀 Быстрый старт

### Автоматическая настройка (рекомендуется)

```bash
# Создает виртуальное окружение и запускает утилиту
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run
```

### Ручная настройка

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
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
```

### Переменные окружения

- `FPGA_TARGET_ARTIFACT` - список стадий через запятую (elab,synth,bitstream)

## 📁 Структура проекта

```
fpga/
├── test_fpga/
│   └── cfg.yaml          # Конфигурация сабмодуля
fpga_pipeline_generator/
├── config/
│   └── default.yaml      # Конфигурация по умолчанию
├── templates/
│   ├── pipeline.j2       # Шаблон пайплайна 
│   └── job.j2           # Шаблон задачи 
└── core/
    ├── generator.py      # Основная логика
    └── parser.py         # Парсер конфигураций
```

## 📝 Формат конфигурации

### cfg.yaml (в сабмодулях) Используется только FPGA_TARGET_ARTIFACT=elab

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

### Генерируемый YAML

```yaml
# Generated FPGA Pipeline
stages:
  - elab

elab_lsio_au_elab_test_fpga:
  stage: elab
  tags: ["devops-elab"]
  script:
    - "echo elab VAR='FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev' TARGET='lsio_au_elab'"
    - "echo 'Executing: make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev'"
    - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev"
  rules:
    - if: "$CI_MERGE_REQUEST_ID"
```



