"""
Утилиты для работы с файлами.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class FileUtils:
    """Утилиты для работы с файлами."""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """Проверяет существование директории и создает её при необходимости."""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"Ошибка создания директории {directory}: {e}")
            return False
    
    @staticmethod
    def validate_yaml_file(file_path: str) -> bool:
        """Проверяет корректность YAML файла."""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True
        except yaml.YAMLError:
            return False
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
        """Находит файлы по шаблону в директории."""
        if not os.path.exists(directory):
            return []
        
        found_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if pattern in file:
                    found_files.append(os.path.join(root, file))
        
        return found_files
    
    @staticmethod
    def read_yaml_safe(file_path: str) -> Dict[str, Any]:
        """Безопасно читает YAML файл."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            return {}
    
    @staticmethod
    def write_yaml_safe(data: Dict[str, Any], file_path: str) -> bool:
        """Безопасно записывает данные в YAML файл."""
        try:
            FileUtils.ensure_directory_exists(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Ошибка записи файла {file_path}: {e}")
            return False
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str = ".") -> str:
        """Получает относительный путь файла."""
        try:
            return os.path.relpath(file_path, base_path)
        except Exception:
            return file_path
    
    @staticmethod
    def backup_file(file_path: str) -> Optional[str]:
        """Создает резервную копию файла."""
        if not os.path.exists(file_path):
            return None
        
        backup_path = f"{file_path}.backup"
        counter = 1
        
        while os.path.exists(backup_path):
            backup_path = f"{file_path}.backup.{counter}"
            counter += 1
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return None