#!/bin/bash

# Скрипт для запуска FPGA Pipeline Generator с fallback генерацией (без Jinja2)

# Проверяем, существует ли виртуальное окружение
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Создаю..."
    python3 -m venv venv
    source venv/bin/activate
    pip install pyyaml
else
    source venv/bin/activate
fi

# Временно переименовываем папку templates, чтобы отключить Jinja2
if [ -d "fpga_pipeline_generator/templates" ]; then
    mv fpga_pipeline_generator/templates fpga_pipeline_generator/templates_backup
    echo "Jinja2 отключен, используется fallback генерация"
fi

# Запускаем утилиту с переданными аргументами
python fpga_gen.py "$@"

# Восстанавливаем папку templates
if [ -d "fpga_pipeline_generator/templates_backup" ]; then
    mv fpga_pipeline_generator/templates_backup fpga_pipeline_generator/templates
fi