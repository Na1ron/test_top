#!/usr/bin/env python3
"""
Упрощенный CLI для FPGA Pipeline Generator.
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fpga_pipeline_generator.main import main

if __name__ == "__main__":
    sys.exit(main())