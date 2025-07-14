# FPGA Pipeline Generator

Утилита для автоматической генерации динамических пайплайнов на основе конфигурационных файлов cfg.yaml из сабмодулей FPGA.

## Описание

Утилита парсит файлы `cfg.yaml` из всех сабмодулей в папке `fpga` и создает YAML конфигурацию для динамического пайплайна. Генерация происходит на основе переменной окружения `FPGA_TARGET_ARTIFACT`, которая определяет, какие стадии (elab, synth, bitstream) должны быть включены в пайплайн.

## Установка зависимостей

```bash
pip install -r requirements.txt
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
# Генерация в файл generated_pipeline.yml (по умолчанию)
python generate_fpga_pipeline.py

# Генерация в указанный файл
python generate_fpga_pipeline.py my_pipeline.yml
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

## Структура проекта

```
.
├── fpga/
│   ├── submodule1/
│   │   └── cfg.yaml
│   ├── submodule2/
│   │   └── cfg.yaml
│   └── ...
├── generate_fpga_pipeline.py
├── requirements.txt
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
  script:
    - echo "Выполняется elab для цели lsio_au_elab"
    - echo "Сабмодуль: test_fpga"
  variables:
    FPGA_STAGE: elab
    FPGA_TARGET: lsio_au_elab
    FPGA_SUBMODULE: test_fpga
    FPGA_BOARD_TYPE: HTG960

synth_lsio_au_test_fpga:
  stage: synth
  script:
    - echo "Выполняется synth для цели lsio_au"
    - echo "Сабмодуль: test_fpga"
  variables:
    FPGA_STAGE: synth
    FPGA_TARGET: lsio_au
    FPGA_SUBMODULE: test_fpga

synth_lsio_au_2_test_fpga:
  stage: synth
  script:
    - echo "Выполняется synth для цели lsio_au_2"
    - echo "Сабмодуль: test_fpga"
    - echo "Опции: --write-netlist --disable-reports"
  variables:
    FPGA_STAGE: synth
    FPGA_TARGET: lsio_au_2
    FPGA_SUBMODULE: test_fpga
    FPGA_BOARD_TYPE: VCU118
    USE_ORIG_MEM: "1"
    FPGA_OPTIONS: --write-netlist --disable-reports
```

## Особенности

1. **Фильтрация по переменной окружения**: Утилита создает только те стадии, которые указаны в `FPGA_TARGET_ARTIFACT`
2. **Поддержка множественных сабмодулей**: Автоматически обнаруживает все сабмодули в папке `fpga`
3. **Наследование переменных**: Переменные из секции `vars` добавляются в конфигурацию задач
4. **Поддержка опций**: Опции из секции `options` передаются в переменную `FPGA_OPTIONS`
5. **Уникальные имена задач**: Имена формируются как `{stage}_{target}_{submodule}`

## Отладка

Для отладки установите переменную окружения с выводом отладочной информации:

```bash
export FPGA_TARGET_ARTIFACT=synth,elab
python generate_fpga_pipeline.py
```

Утилита выведет информацию о найденных сабмодулях и созданных задачах.