"""
FPGA Pipeline Generator

Пакет для автоматической генерации динамических CI/CD пайплайнов
на основе конфигурационных файлов fpga-builds.yaml из сабмодулей FPGA.
"""

__version__ = "1.0.0"
__author__ = "Vladimir Kozlov"

from fpga_pipeline_generator.core.generator import FPGAPipelineGenerator
from fpga_pipeline_generator.core.parser import ConfigParser
from fpga_pipeline_generator.core.config_loader import ConfigLoader

__all__ = ["FPGAPipelineGenerator", "ConfigParser", "ConfigLoader"]
