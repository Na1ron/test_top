#!/usr/bin/env python3
"""
Точка входа для FPGA Pipeline Generator.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .core.generator import FPGAPipelineGenerator
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Создает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="FPGA Pipeline Generator - генерирует динамические CI/CD пайплайны для FPGA проектов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Базовое использование (с переменной окружения FPGA_TARGET_ARTIFACT)
  python -m fpga_pipeline_generator
  
  # Указание выходного файла
  python -m fpga_pipeline_generator -o my_pipeline.yml
  
  # Использование пользовательской конфигурации
  python -m fpga_pipeline_generator -c custom_config.yaml
  
  # Установка целевых артефактов через аргумент
  python -m fpga_pipeline_generator --stages elab,synth
  
Переменные окружения:
  FPGA_TARGET_ARTIFACT - список стадий через запятую (elab,synth,bitstream)
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Путь к выходному файлу (по умолчанию: generated_pipeline.yml)'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Путь к пользовательскому файлу конфигурации'
    )
    
    parser.add_argument(
        '--stages',
        type=str,
        help='Список стадий через запятую (переопределяет FPGA_TARGET_ARTIFACT)'
    )
    
    parser.add_argument(
        '--fpga-dir',
        type=str,
        default='fpga',
        help='Директория с FPGA сабмодулями (по умолчанию: fpga)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Не сохранять файл, только вывести результат'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'FPGA Pipeline Generator {__version__}'
    )
    
    return parser


def setup_environment(args) -> None:
    """Настраивает переменные окружения на основе аргументов."""
    import os
    
    if args.stages:
        os.environ['FPGA_TARGET_ARTIFACT'] = args.stages
        if args.verbose:
            print(f"Установлена FPGA_TARGET_ARTIFACT={args.stages}")


def main() -> int:
    """Основная функция."""
    parser = create_parser()
    args = parser.parse_args()
    
    print("FPGA Pipeline Generator")
    print("=" * 50)
    print(f"Версия: {__version__}")
    
    if args.verbose:
        print(f"Аргументы: {vars(args)}")
    
    try:
        # Настраиваем окружение
        setup_environment(args)
        
        # Создаем генератор
        generator = FPGAPipelineGenerator(args.config)
        
        # Генерируем пайплайн
        pipeline_content = generator.generate_pipeline()
        
        if not pipeline_content:
            print("Не удалось сгенерировать пайплайн")
            return 1
        
        # Выводим или сохраняем результат
        if args.dry_run:
            print("\nСгенерированный пайплайн:")
            print("-" * 50)
            print(pipeline_content)
        else:
            success = generator.save_pipeline(pipeline_content, args.output)
            if not success:
                return 1
        
        print("\nГенерация завершена успешно!")
        return 0
        
    except KeyboardInterrupt:
        print("\nОперация прервана пользователем")
        return 130
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())