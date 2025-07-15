#!/bin/bash

# Скрипт для запуска FPGA Pipeline Generator через виртуальное окружение

# Проверяем, существует ли виртуальное окружение
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Создаю..."
    python3 -m venv venv
    source venv/bin/activate
    pip install pyyaml
else
    source venv/bin/activate
fi

# Запускаем утилиту с переданными аргументами
python fpga_gen.py "$@"