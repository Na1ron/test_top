"""
Основной модуль генерации пайплайнов.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Отключаем Jinja2 по умолчанию для корректного YAML форматирования
JINJA2_AVAILABLE = False

from .config_loader import ConfigLoader
from .parser import ConfigParser


class FPGAPipelineGenerator:
    """Основной класс для генерации FPGA пайплайнов."""
    
    def __init__(self, user_config_path: Optional[str] = None):
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_config(user_config_path)
        
        # Получаем настройки из конфигурации
        file_search_config = self.config.get('file_search', {})
        fpga_dir = file_search_config.get('fpga_dir', 'fpga')
        config_filename = file_search_config.get('config_filename', 'cfg.yaml')
        
        self.parser = ConfigParser(fpga_dir, config_filename)
        
        # Отключаем Jinja2 для корректного YAML форматирования
        self.jinja_env = None
    
    def get_target_stages(self) -> List[str]:
        """Получает целевые стадии из переменной окружения."""
        stages = self.parser.get_environment_artifacts()
        if not stages:
            print("Переменная окружения FPGA_TARGET_ARTIFACT не установлена")
            return []
        
        supported_stages = self.config_loader.get_supported_stages(self.config)
        return self.parser.validate_stages(stages, supported_stages)
    
    def generate_job_name(self, stage: str, target: str, submodule: str) -> str:
        """Генерирует имя задачи."""
        return f"{stage}_{target}_{submodule}"
    
    def prepare_job_context(self, stage: str, target_config: Dict[str, Any], submodule: str) -> Dict[str, Any]:
        """Подготавливает контекст для генерации задачи."""
        stage_config = self.config_loader.get_stage_config(stage, self.config)
        default_vars = self.config.get('default_variables', {})
        default_rules = self.config.get('default_rules', [])
        
        target_name = target_config['target']
        target_vars = target_config['variables']
        target_options = target_config['options']
        
        # Формируем аргументы для make
        make_args = ""
        if target_vars:
            for var_name, var_value in target_vars.items():
                make_args += f" {var_name}={var_value}"
        
        if target_options:
            make_args += " " + " ".join(target_options)
        
        # Формируем переменные задачи
        job_variables = {
            'FPGA_STAGE': stage,
            'FPGA_TARGET': target_name,
            'FPGA_SUBMODULE': submodule,
            **default_vars,
            **target_vars
        }
        
        if target_options:
            job_variables['FPGA_OPTIONS'] = " ".join(target_options)
        
        # Формируем строки для команды echo
        vars_string = ""
        if target_vars:
            vars_parts = []
            for var_name, var_value in target_vars.items():
                vars_parts.append(f"{var_name}={var_value}")
            vars_string = " ".join(vars_parts)
        
        options_string = ""
        if target_options:
            options_string = " ".join(target_options)
        
        return {
            'job_name': self.generate_job_name(stage, target_name, submodule),
            'stage': stage,
            'target_name': target_name,
            'tags': stage_config.get('tags', [f"fpga-{stage}"]),
            'make_target': stage_config.get('make_target', stage),
            'make_args': make_args.strip(),
            'makefile_path': default_vars.get('MAKEFILE_PATH', 'Makefile'),
            'target_vars': target_vars,
            'target_options': " ".join(target_options) if target_options else None,
            'vars_string': vars_string if vars_string else None,
            'options_string': options_string if options_string else None,
            'rules': default_rules,
            'job_variables': job_variables
        }
    
    def render_job_with_template(self, job_context: Dict[str, Any]) -> str:
        """Рендерит задачу используя Jinja2 шаблон."""
        if not self.jinja_env:
            return self._render_job_fallback(job_context)
        
        try:
            template = self.jinja_env.get_template('job.j2')
            return template.render(**job_context)
        except Exception as e:
            print(f"Ошибка рендеринга шаблона задачи: {e}")
            return self._render_job_fallback(job_context)
    
    def _render_job_fallback(self, job_context: Dict[str, Any]) -> str:
        """Запасной способ генерации задачи без Jinja2."""
        job_name = job_context['job_name']
        stage = job_context['stage']
        target_name = job_context['target_name']
        tags = job_context['tags']
        make_target = job_context['make_target']
        make_args = job_context['make_args']
        makefile_path = job_context['makefile_path']
        vars_string = job_context.get('vars_string', '')
        options_string = job_context.get('options_string', '')
        job_variables = job_context.get('job_variables', {})
        
        # Формируем echo команду с данными из cfg.yaml
        echo_parts = [stage]
        if vars_string:
            echo_parts.append(f"VAR='{vars_string}'")
        if options_string:
            echo_parts.append(f"OPTIONS='{options_string}'")
        echo_parts.append(f"TARGET='{target_name}'")
        echo_command = " ".join(echo_parts)
        
        # Форматируем теги как YAML список
        tags_yaml = "[" + ", ".join([f'"{tag}"' for tag in tags]) + "]"
        
        job_yaml = f"""{job_name}:
  stage: {stage}
  tags: {tags_yaml}
  script:
    - "echo {echo_command}"
    - "echo 'Executing: make -f {makefile_path} {make_target} {make_args}'"
"""
        
        # Добавляем export команды для переменных
        target_vars = job_context.get('target_vars', {})
        for var_name, var_value in target_vars.items():
            job_yaml += f"    - \"export {var_name}={var_value}\"\n"
        
        job_yaml += f"    - \"make -f {makefile_path} {make_target} {make_args}\"\n"
        
        # Добавляем rules
        job_yaml += """  rules:
    - if: "$CI_MERGE_REQUEST_ID"
"""
        
        # Добавляем variables если есть
        if job_variables:
            job_yaml += "  variables:\n"
            for var_name, var_value in job_variables.items():
                job_yaml += f"    {var_name}: \"{var_value}\"\n"
        
        return job_yaml
    
    def generate_jobs(self, parsed_data: Dict[str, Dict[str, List[Dict[str, Any]]]], stages: List[str]) -> List[str]:
        """Генерирует все задачи."""
        jobs = []
        
        for submodule_name, submodule_data in parsed_data.items():
            for stage in stages:
                if stage in submodule_data:
                    targets = submodule_data[stage]
                    
                    for target_config in targets:
                        job_context = self.prepare_job_context(stage, target_config, submodule_name)
                        job_yaml = self.render_job_with_template(job_context)
                        jobs.append(job_yaml)
        
        return jobs
    
    def prepare_pipeline_context(self, stages: List[str], jobs: List[str]) -> Dict[str, Any]:
        """Подготавливает контекст для генерации пайплайна."""
        from .. import __version__
        
        global_variables = self.config.get('default_variables', {}).copy()
        global_variables['FPGA_TARGET_ARTIFACT'] = ','.join(stages)
        
        return {
            'generator_version': __version__,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'target_artifacts': stages,
            'stages': stages,
            'global_variables': global_variables,
            'jobs': jobs
        }
    
    def render_pipeline_with_template(self, pipeline_context: Dict[str, Any]) -> str:
        """Рендерит пайплайн используя Jinja2 шаблон."""
        if not self.jinja_env:
            return self._render_pipeline_fallback(pipeline_context)
        
        try:
            template = self.jinja_env.get_template('pipeline.j2')
            return template.render(**pipeline_context)
        except Exception as e:
            print(f"Ошибка рендеринга шаблона пайплайна: {e}")
            return self._render_pipeline_fallback(pipeline_context)
    
    def _render_pipeline_fallback(self, pipeline_context: Dict[str, Any]) -> str:
        """Запасной способ генерации пайплайна без Jinja2."""
        stages = pipeline_context['stages']
        jobs = pipeline_context['jobs']
        
        pipeline_yaml = f"""# Generated FPGA Pipeline
stages:
{chr(10).join([f'  - {stage}' for stage in stages])}

{chr(10).join(jobs)}
"""
        return pipeline_yaml
    
    def generate_pipeline(self) -> Optional[str]:
        """Генерирует полный пайплайн."""
        # Получаем целевые стадии
        stages = self.get_target_stages()
        if not stages:
            print("Установите переменную окружения FPGA_TARGET_ARTIFACT")
            print("Например: export FPGA_TARGET_ARTIFACT=synth,elab")
            return None
        
        print(f"Целевые артефакты: {stages}")
        
        # Парсим сабмодули
        parsed_data = self.parser.parse_all_submodules(stages)
        if not parsed_data:
            print("Не найдено данных для генерации пайплайна")
            return None
        
        # Генерируем задачи
        jobs = self.generate_jobs(parsed_data, stages)
        if not jobs:
            print("Не создано ни одной задачи")
            return None
        
        print(f"Создано задач: {len(jobs)}")
        
        # Генерируем пайплайн
        pipeline_context = self.prepare_pipeline_context(stages, jobs)
        return self.render_pipeline_with_template(pipeline_context)
    
    def save_pipeline(self, pipeline_content: str, output_file: Optional[str] = None) -> bool:
        """Сохраняет пайплайн в файл."""
        if not output_file:
            output_config = self.config.get('output', {})
            output_file = output_config.get('default_filename', 'generated_pipeline.yml')
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pipeline_content)
            print(f"Конфигурация пайплайна сохранена в {output_file}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return False