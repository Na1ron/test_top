"""
FPGA Pipeline Generator

Пакет для автоматической генерации динамических CI/CD пайплайнов 
на основе конфигурационных файлов cfg.yaml из сабмодулей FPGA.
"""

__version__ = "1.0.0"
__author__ = "FPGA Pipeline Generator Team"

from .core.generator import FPGAPipelineGenerator
from .core.parser import ConfigParser
from .core.config_loader import ConfigLoader

__all__ = [
    "FPGAPipelineGenerator",
    "ConfigParser", 
    "ConfigLoader"
]