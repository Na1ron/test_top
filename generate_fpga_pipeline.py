#!/usr/bin/env python3
"""
FPGA Pipeline Generator

Утилита для парсинга cfg.yaml из сабмодулей в папке fpga 
и генерации динамического пайплайна на основе переменной окружения FPGA_TARGET_ARTIFACT.
"""

import os
import yaml
import glob
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class FPGAPipelineGenerator:
    def __init__(self, fpga_dir: str = "fpga"):
        self.fpga_dir = fpga_dir
        self.stages = ["elab", "synth", "bitstream"]
        
    def find_submodules(self) -> List[str]:
        """Находит все сабмодули в папке fpga."""
        if not os.path.exists(self.fpga_dir):
            print(f"Папка {self.fpga_dir} не найдена")
            return []
            
        submodules = []
        for item in os.listdir(self.fpga_dir):
            submodule_path = os.path.join(self.fpga_dir, item)
            if os.path.isdir(submodule_path):
                submodules.append(submodule_path)
                
        return submodules
    
    def find_cfg_yaml(self, submodule_path: str) -> Optional[str]:
        """Ищет файл cfg.yaml в сабмодуле."""
        cfg_path = os.path.join(submodule_path, "cfg.yaml")
        if os.path.exists(cfg_path):
            return cfg_path
        return None
    
    def parse_cfg_yaml(self, cfg_path: str) -> Dict[str, Any]:
        """Парсит cfg.yaml файл."""
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Файл {cfg_path} не найден")
            return {}
        except yaml.YAMLError as e:
            print(f"Ошибка парсинга YAML: {e}")
            return {}
    
    def get_target_artifacts(self) -> List[str]:
        """Получает список целевых артефактов из переменной окружения."""
        artifacts = os.getenv('FPGA_TARGET_ARTIFACT', '')
        if not artifacts:
            print("Переменная окружения FPGA_TARGET_ARTIFACT не установлена")
            return []
        
        return [artifact.strip() for artifact in artifacts.split(',') if artifact.strip()]
    
    def create_job_config(self, stage: str, target_info: Dict[str, Any], submodule_name: str) -> Dict[str, Any]:
        """Создает конфигурацию для одной задачи."""
        target_name = target_info.get('target', 'unknown')
        job_name = f"{stage}_{target_name}"
        
        job_config = {
            'stage': stage,
            'script': [
                f'echo "Выполняется {stage} для цели {target_name}"',
                f'echo "Сабмодуль: {submodule_name}"'
            ],
            'variables': {
                'FPGA_STAGE': stage,
                'FPGA_TARGET': target_name,
                'FPGA_SUBMODULE': submodule_name
            }
        }
        
        # Добавляем переменные из конфигурации
        if 'vars' in target_info:
            for var in target_info['vars']:
                if '=' in var:
                    key, value = var.split('=', 1)
                    job_config['variables'][key] = value
        
        # Добавляем опции в скрипт
        if 'options' in target_info:
            options_str = ' '.join(target_info['options'])
            job_config['script'].append(f'echo "Опции: {options_str}"')
            job_config['variables']['FPGA_OPTIONS'] = options_str
        
        return job_config
    
    def generate_pipeline(self) -> Dict[str, Any]:
        """Генерирует конфигурацию пайплайна."""
        target_artifacts = self.get_target_artifacts()
        if not target_artifacts:
            return {}
        
        submodules = self.find_submodules()
        if not submodules:
            print("Сабмодули не найдены")
            return {}
        
        pipeline_config = {
            'stages': target_artifacts,
            'variables': {
                'FPGA_TARGET_ARTIFACT': ','.join(target_artifacts)
            }
        }
        
        job_configs = {}
        
        for submodule_path in submodules:
            submodule_name = os.path.basename(submodule_path)
            cfg_path = self.find_cfg_yaml(submodule_path)
            
            if not cfg_path:
                print(f"cfg.yaml не найден в сабмодуле {submodule_name}")
                continue
            
            cfg_data = self.parse_cfg_yaml(cfg_path)
            if not cfg_data:
                continue
            
            print(f"Обрабатывается сабмодуль: {submodule_name}")
            
            # Создаем задачи для каждой стадии, указанной в FPGA_TARGET_ARTIFACT
            for stage in target_artifacts:
                if stage in cfg_data and stage in self.stages:
                    targets = cfg_data[stage]
                    
                    for i, target_info in enumerate(targets):
                        target_name = target_info.get('target', f'unknown_{i}')
                        job_name = f"{stage}_{target_name}_{submodule_name}"
                        
                        job_config = self.create_job_config(stage, target_info, submodule_name)
                        job_configs[job_name] = job_config
                        
                        print(f"  Создана задача: {job_name}")
                else:
                    if stage in self.stages:
                        print(f"  Стадия '{stage}' не найдена в cfg.yaml сабмодуля {submodule_name}")
        
        # Объединяем конфигурацию пайплайна с задачами
        pipeline_config.update(job_configs)
        
        return pipeline_config
    
    def save_pipeline(self, pipeline_config: Dict[str, Any], output_file: str = "generated_pipeline.yml"):
        """Сохраняет конфигурацию пайплайна в YAML файл."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(pipeline_config, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            print(f"Конфигурация пайплайна сохранена в {output_file}")
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")


def main():
    """Основная функция."""
    generator = FPGAPipelineGenerator()
    
    print("FPGA Pipeline Generator")
    print("=" * 50)
    
    # Показываем текущие настройки
    target_artifacts = generator.get_target_artifacts()
    print(f"Целевые артефакты из FPGA_TARGET_ARTIFACT: {target_artifacts}")
    
    if not target_artifacts:
        print("Установите переменную окружения FPGA_TARGET_ARTIFACT")
        print("Например: export FPGA_TARGET_ARTIFACT=synth,elab")
        sys.exit(1)
    
    # Генерируем пайплайн
    pipeline_config = generator.generate_pipeline()
    
    if not pipeline_config:
        print("Не удалось сгенерировать конфигурацию пайплайна")
        sys.exit(1)
    
    # Сохраняем результат
    output_file = sys.argv[1] if len(sys.argv) > 1 else "generated_pipeline.yml"
    generator.save_pipeline(pipeline_config, output_file)
    
    print("\nГенерация завершена!")


if __name__ == "__main__":
    main()