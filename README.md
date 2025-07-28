# FPGA Pipeline Generator

Генератор динамических CI/CD пайплайнов для FPGA проектов на основе конфигурационных файлов.

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
```

### Ручная настройка

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -e .

# Запуск утилиты
export FPGA_TARGET_ARTIFACT=elab (задание тестовой переменной окружения)
fpga-pipeline-gen --dry-run
```

### Переменные окружения

- `FPGA_TARGET_ARTIFACT` - список стадий через запятую (elab,synth,bitstream)


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

### Пример сгенерированного YAML с переменной окружения FPGA_TARGET_ARTIFACT=elab

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



