#!/usr/bin/env python3
"""
Упрощенный CLI для FPGA Pipeline Generator.
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from fpga_pipeline_generator.main import main

if __name__ == "__main__":
    sys.exit(main())