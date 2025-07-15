# Использование FPGA Pipeline Generator через виртуальное окружение

## Быстрый старт

### 1. Автоматическая настройка (рекомендуется)

Используйте готовый скрипт для автоматической настройки и запуска:

```bash
# Создает venv, устанавливает зависимости и запускает утилиту
./run_fpga_gen.sh --dry-run
```

### 2. Ручная настройка

Если нужно настроить окружение вручную:

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate

# Установка зависимостей
pip install jinja2 pyyaml

# Запуск утилиты
python fpga_gen.py --dry-run
```

## Доступные скрипты

### `run_fpga_gen.sh` - Полная версия с Jinja2
- Автоматически создает виртуальное окружение
- Устанавливает Jinja2 и PyYAML
- Использует шаблоны Jinja2 для генерации

### `run_fpga_gen_fallback.sh` - Fallback версия
- Автоматически создает виртуальное окружение
- Устанавливает только PyYAML
- Использует встроенную генерацию (рекомендуется для корректного YAML)

## Примеры использования

### Базовое использование
```bash
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen_fallback.sh --dry-run
```

### С указанием выходного файла
```bash
export FPGA_TARGET_ARTIFACT=elab,synth
./run_fpga_gen_fallback.sh -o my_pipeline.yml
```

### С подробным выводом
```bash
export FPGA_TARGET_ARTIFACT=elab
./run_fpga_gen_fallback.sh --dry-run --verbose
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
│   ├── pipeline.j2       # Шаблон пайплайна
│   └── job.j2           # Шаблон задачи
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

### Проблема: "Jinja2 не установлен"
Используйте fallback версию:
```bash
./run_fpga_gen_fallback.sh --dry-run
```

### Проблема: Неправильное форматирование YAML
Используйте fallback версию, которая генерирует корректный YAML:
```bash
./run_fpga_gen_fallback.sh --dry-run
```