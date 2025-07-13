"""
Модуль для загрузки и обработки конфигурационных файлов.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Класс для загрузки конфигурационных файлов."""
    
    def __init__(self):
        self.default_config = None
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Загружает конфигурацию по умолчанию."""
        config_path = Path(__file__).parent.parent / "config" / "default.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.default_config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации {config_path} не найден")
            self.default_config = {}
        except yaml.YAMLError as e:
            print(f"Ошибка парсинга конфигурации: {e}")
            self.default_config = {}
    
    def load_user_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Загружает пользовательскую конфигурацию."""
        if not config_path:
            return {}
        
        if not os.path.exists(config_path):
            print(f"Пользовательский конфиг {config_path} не найден")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Ошибка парсинга пользовательского конфига: {e}")
            return {}
    
    def merge_configs(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Объединяет конфигурацию по умолчанию с пользовательской."""
        if not self.default_config:
            return user_config
        
        merged = self.default_config.copy()
        
        def deep_merge(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
            """Рекурсивно объединяет словари."""
            result = default.copy()
            
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            
            return result
        
        return deep_merge(merged, user_config)
    
    def get_config(self, user_config_path: Optional[str] = None) -> Dict[str, Any]:
        """Получает итоговую конфигурацию."""
        user_config = self.load_user_config(user_config_path)
        return self.merge_configs(user_config)
    
    def get_stage_config(self, stage: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Получает конфигурацию для конкретной стадии."""
        stages_config = config.get('stages', {})
        return stages_config.get(stage, {})
    
    def get_supported_stages(self, config: Dict[str, Any]) -> list:
        """Получает список поддерживаемых стадий."""
        return config.get('supported_stages', ['elab', 'synth', 'bitstream'])
    
    def get_template_path(self, template_name: str, config: Dict[str, Any]) -> Path:
        """Получает путь к шаблону."""
        templates_config = config.get('templates', {})
        template_file = templates_config.get(template_name, f"{template_name}.j2")
        
        templates_dir = Path(__file__).parent.parent / "templates"
        return templates_dir / template_file