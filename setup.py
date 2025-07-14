#!/usr/bin/env python3
"""
Setup script для FPGA Pipeline Generator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README файл
this_directory = Path(__file__).parent
long_description = (this_directory / "FPGA_PIPELINE_README.md").read_text(encoding='utf-8')

# Читаем requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding='utf-8').strip().split('\n')

setup(
    name="fpga-pipeline-generator",
    version="1.0.0",
    author="FPGA Pipeline Generator Team",
    author_email="dev@example.com",
    description="Генератор динамических CI/CD пайплайнов для FPGA проектов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/fpga-pipeline-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fpga-pipeline-gen=fpga_pipeline_generator.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fpga_pipeline_generator": [
            "templates/*.j2",
            "config/*.yaml",
        ],
    },
    zip_safe=False,
)