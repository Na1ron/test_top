"""
Модуль для парсинга cfg.yaml файлов из сабмодулей.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class ConfigParser:
    """Класс для парсинга конфигурационных файлов cfg.yaml."""

    def __init__(self, fpga_dir: str = "fpga", config_filename: str = "cfg.yaml"):
        self.fpga_dir = fpga_dir
        self.config_filename = config_filename

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
        cfg_path = os.path.join(submodule_path, self.config_filename)
        if os.path.exists(cfg_path):
            return cfg_path
        return None

    def parse_cfg_yaml(self, cfg_path: str) -> Dict[str, Any]:
        """Парсит cfg.yaml файл."""
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Файл {cfg_path} не найден")
            return {}
        except yaml.YAMLError as e:
            print(f"Ошибка парсинга YAML {cfg_path}: {e}")
            return {}

    def extract_target_info(
        self, target_config: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str], List[str]]:
        """Извлекает информацию о цели из конфигурации."""
        target_name = target_config.get("target", "unknown")

        # Парсим переменные - поддерживаем как 'vars', так и 'variables'
        variables = {}
        if "variables" in target_config:
            # Поддержка как dict, так и list формата
            if isinstance(target_config["variables"], dict):
                variables = target_config["variables"]
            elif isinstance(target_config["variables"], list):
                for var in target_config["variables"]:
                    if isinstance(var, str) and "=" in var:
                        key, value = var.split("=", 1)
                        variables[key.strip()] = value.strip()
            else:
                variables = {}  # если формат неизвестен
        elif "vars" in target_config:
            for var in target_config["vars"]:
                if isinstance(var, str) and "=" in var:
                    key, value = var.split("=", 1)
                    variables[key.strip()] = value.strip()

        # Извлекаем опции
        options = target_config.get("options", [])

        return target_name, variables, options

    def get_targets_for_stage(
        self, cfg_data: Dict[str, Any], stage: str
    ) -> List[Dict[str, Any]]:
        """Получает список целей для указанной стадии."""
        if stage not in cfg_data:
            return []

        stage_data = cfg_data[stage]
        if not isinstance(stage_data, list):
            return []

        return stage_data

    def parse_all_submodules(
        self, target_stages: List[str]
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Парсит все сабмодули и возвращает структуру:
        {
            'submodule_name': {
                'stage_name': [target_configs...],
                'submodule_path': 'path/to/submodule'
            }
        }
        """
        result = {}
        submodules = self.find_submodules()

        for submodule_path in submodules:
            submodule_name = os.path.basename(submodule_path)
            cfg_path = self.find_cfg_yaml(submodule_path)

            if not cfg_path:
                print(f"cfg.yaml не найден в сабмодуле {submodule_name}")
                continue

            cfg_data = self.parse_cfg_yaml(cfg_path)
            if not cfg_data:
                continue

            submodule_targets = {}

            for stage in target_stages:
                targets = self.get_targets_for_stage(cfg_data, stage)
                if targets:
                    # Обогащаем каждую цель дополнительной информацией
                    enriched_targets = []
                    for target_config in targets:
                        target_name, variables, options = self.extract_target_info(
                            target_config
                        )

                        enriched_target = {
                            "target": target_name,
                            "variables": variables,
                            "options": options,
                            "original_config": target_config,
                        }
                        enriched_targets.append(enriched_target)

                    submodule_targets[stage] = enriched_targets

            if submodule_targets:
                # Добавляем путь к сабмодулю
                submodule_targets["submodule_path"] = submodule_path
                result[submodule_name] = submodule_targets
                print(f"Обработан сабмодуль: {submodule_name}")

        return result

    def get_environment_artifacts(self) -> List[str]:
        """Получает список целевых артефактов из переменной окружения."""
        artifacts = os.getenv("FPGA_TARGET_ARTIFACT", "")
        if not artifacts:
            return []

        return [
            artifact.strip() for artifact in artifacts.split(",") if artifact.strip()
        ]

    def validate_stages(
        self, stages: List[str], supported_stages: List[str]
    ) -> List[str]:
        """Проверяет и фильтрует поддерживаемые стадии."""
        valid_stages = []
        for stage in stages:
            if stage in supported_stages:
                valid_stages.append(stage)
            else:
                print(
                    f"Предупреждение: стадия '{stage}' не поддерживается. Поддерживаемые: {supported_stages}"
                )

        return valid_stages
