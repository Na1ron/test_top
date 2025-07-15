# Использование FPGA Pipeline Generator через виртуальное окружение

## Быстрый старт

### Автоматическая настройка (рекомендуется)

Используйте готовый скрипт для автоматической настройки и запуска:

```bash
# Создает venv, устанавливает зависимости и запускает утилиту
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run
```

### Ручная настройка

Если нужно настроить окружение вручную:

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate

# Установка зависимостей
pip install pyyaml

# Запуск утилиты
export FPGA_TARGET_ARTIFACT=elab
python fpga_gen.py --dry-run
```

## Доступные скрипты

### `run_fpga_gen.sh` - Основной скрипт
- Автоматически создает виртуальное окружение
- Устанавливает PyYAML
- Использует встроенную генерацию с корректным YAML форматированием

## Примеры использования

### Базовое использование
```bash
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run
```

### С указанием выходного файла
```bash
export FPGA_TARGET_ARTIFACT=elab,synth
./run_fpga_gen.sh -o my_pipeline.yml
```

### С подробным выводом
```bash
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen.sh --dry-run --verbose
```

## Переменные окружения

- `FPGA_TARGET_ARTIFACT` - список стадий через запятую (elab,synth,bitstream)

## Структура проекта

```
fpga/
├── test_fpga/
│   └── cfg.yaml          # Конфигурация для тестового сабмодуля
fpga_pipeline_generator/
├── config/
│   └── default.yaml      # Конфигурация по умолчанию
├── templates/
│   ├── pipeline.j2       # Шаблон пайплайна (не используется)
│   └── job.j2           # Шаблон задачи (не используется)
└── core/
    ├── generator.py      # Основная логика генерации
    └── parser.py         # Парсер конфигураций
```

## Формат cfg.yaml

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

## Устранение неполадок

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
Утилита теперь использует встроенную генерацию с корректным YAML форматированием.