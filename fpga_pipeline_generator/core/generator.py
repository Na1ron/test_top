"""
Основной модуль генерации пайплайнов.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

# Отключаем Jinja2 по умолчанию для корректного YAML форматирования
JINJA2_AVAILABLE = False

from .config_loader import ConfigLoader
from .parser import ConfigParser
from jinja2 import Environment, FileSystemLoader
import os


class FPGAPipelineGenerator:
    """Основной класс для генерации FPGA пайплайнов."""

    def __init__(self, user_config_path: Optional[str] = None):
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_config(user_config_path)

        # Получаем настройки из конфигурации
        file_search_config = self.config.get("file_search", {})
        fpga_dir = file_search_config.get("fpga_dir", "fpga")
        config_filename = file_search_config.get("config_filename", "cfg.yaml")

        self.parser = ConfigParser(fpga_dir, config_filename)
        # Инициализация Jinja2 с абсолютным путем к шаблонам
        template_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "templates")
        )
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Добавляем пользовательские фильтры для работы с путями
        self.jinja_env.filters["dirname"] = lambda path: os.path.dirname(path)
        self.jinja_env.filters["basename"] = lambda path: os.path.basename(path)

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

    def prepare_job_context(
        self,
        stage: str,
        target_config: Dict[str, Any],
        submodule: str,
        submodule_path: str,
    ) -> Dict[str, Any]:
        """Подготавливает контекст для генерации задачи."""
        stage_config = self.config_loader.get_stage_config(stage, self.config)
        default_vars = self.config.get("default_variables", {})
        default_rules = self.config.get("default_rules", [])

        target_name = target_config["target"]
        target_vars = target_config["variables"]
        target_options = target_config["options"]

        # Формируем аргументы для make
        make_args = ""
        if target_vars:
            for var_name, var_value in target_vars.items():
                make_args += f" {var_name}={var_value}"

        if target_options:
            make_args += " " + " ".join(target_options)

        # Формируем переменные задачи
        job_variables = {
            "FPGA_STAGE": stage,
            "FPGA_TARGET": target_name,
            "FPGA_SUBMODULE": submodule,
            **default_vars,
            **target_vars,
        }

        if target_options:
            job_variables["FPGA_OPTIONS"] = " ".join(target_options)

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

        # Формируем CLI-строку для переменных
        variables_cli = ""
        if target_vars:
            variables_cli = " ".join([f"--var {k}={v}" for k, v in target_vars.items()])

        # Формируем CLI-строку для опций
        options_cli = ""
        if target_options:
            options_cli = " ".join(target_options)

        # Формируем путь к Makefile относительно сабмодуля
        makefile_path = os.path.join(
            submodule_path, default_vars.get("MAKEFILE_PATH", "Makefile")
        )

        return {
            "job_name": self.generate_job_name(stage, target_name, submodule),
            "stage": stage,
            "target_name": target_name,
            "tags": stage_config.get("tags", [f"fpga-{stage}"]),
            "make_target": stage_config.get("make_target", stage),
            "make_args": make_args.strip(),
            "makefile_path": makefile_path,
            "target_vars": target_vars,
            "target_options": " ".join(target_options) if target_options else None,
            "vars_string": vars_string if vars_string else None,
            "options_string": options_string if options_string else None,
            "variables_cli": variables_cli if variables_cli else None,
            "options_cli": options_cli if options_cli else None,
            "rules": default_rules,
            "job_variables": job_variables,
        }

    def render_job_with_template(self, job_context: Dict[str, Any]) -> str:
        """Рендерит задачу используя Jinja2 шаблон."""
        template = self.jinja_env.get_template("job.j2")
        return template.render(**job_context)

    def generate_jobs(
        self, parsed_data: Dict[str, Dict[str, List[Dict[str, Any]]]], stages: List[str]
    ) -> List[str]:
        """Генерирует все задачи."""
        jobs = []

        for submodule_name, submodule_data in parsed_data.items():
            # Получаем путь к сабмодулю
            submodule_path = submodule_data.get("submodule_path", "")
            for stage in stages:
                if stage in submodule_data:
                    targets = submodule_data[stage]

                    for target_config in targets:
                        job_context = self.prepare_job_context(
                            stage, target_config, submodule_name, submodule_path
                        )
                        job_yaml = self.render_job_with_template(job_context)
                        jobs.append(job_yaml)

        return jobs

    def prepare_pipeline_context(
        self, stages: List[str], jobs: List[str]
    ) -> Dict[str, Any]:
        """Подготавливает контекст для генерации пайплайна."""
        from .. import __version__

        global_variables = self.config.get("default_variables", {}).copy()
        global_variables["FPGA_TARGET_ARTIFACT"] = ",".join(stages)

        return {
            "generator_version": __version__,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_artifacts": stages,
            "stages": stages,
            "global_variables": global_variables,
            "jobs": jobs,
        }

    def render_pipeline_with_template(self, pipeline_context: Dict[str, Any]) -> str:
        """Рендерит пайплайн используя Jinja2 шаблон."""
        template = self.jinja_env.get_template("pipeline.j2")
        return template.render(**pipeline_context)

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

    def save_pipeline(
        self, pipeline_content: str, output_file: Optional[str] = None
    ) -> bool:
        """Сохраняет пайплайн в файл."""
        if not output_file:
            output_config = self.config.get("output", {})
            output_file = output_config.get(
                "default_filename", "generated_pipeline.yml"
            )

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(pipeline_content)
            print(f"Конфигурация пайплайна сохранена в {output_file}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return False
