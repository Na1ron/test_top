"""
Модуль для загрузки и обработки конфигурационных файлов.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from copy import deepcopy

@dataclass(frozen=True)
class StageConfig:
    tags: List[str]
    make_target: str
    description: str

@dataclass(frozen=True)
class TemplatesConfig:
    pipeline: str
    job: str

@dataclass(frozen=True)
class OutputConfig:
    indent: int
    default_filename: str

@dataclass(frozen=True)
class FileSearchConfig:
    fpga_dir: str
    config_filename: str

@dataclass(frozen=True)
class DefaultConfig:
    stages: Dict[str, StageConfig]
    default_rules: List[dict]
    default_variables: Dict[str, str]
    templates: TemplatesConfig
    output: OutputConfig
    supported_stages: List[str]
    file_search: FileSearchConfig

DEFAULT_CONFIG = DefaultConfig(
    stages={
        "elab": StageConfig(tags=["soc-fpga-elab"], make_target="elab", description="FPGA Elaboration"),
        "synth": StageConfig(tags=["soc-fpga-synth"], make_target="synth", description="FPGA Synthesis"),
        "bitstream": StageConfig(tags=["soc-fpga-synth"], make_target="bitstream", description="FPGA Bitstream Generation"),
    },
    default_rules=[{"when": "always"}],
    default_variables={
        "FPGA_WORKSPACE": "/workspace",
        "MAKEFILE_PATH": "Makefile",
    },
    templates=TemplatesConfig(pipeline="pipeline.j2", job="job.j2"),
    output=OutputConfig(indent=2, default_filename="generated_pipeline.yml"),
    supported_stages=["elab", "synth", "bitstream"],
    file_search=FileSearchConfig(fpga_dir="fpga", config_filename="cfg.yaml"),
)

class ConfigLoader:
    """Класс для загрузки конфигурационных файлов."""
    def __init__(self):
        self.default_config = DEFAULT_CONFIG

    def load_user_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        if not config_path:
            return {}
        path = Path(config_path)
        if not path.exists():
            print(f"Пользовательский конфиг {config_path} не найден")
            return {}
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Ошибка парсинга пользовательского конфига: {e}")
            return {}

    def merge_configs(self, user_config: Dict[str, Any]) -> DefaultConfig:
        # Преобразуем user_config в структуру DefaultConfig, переопределяя только те поля, что есть в user_config
        base = deepcopy(self.default_config)
        # stages
        if 'stages' in user_config:
            stages = {**{k: v for k, v in base.stages.items()}, **{k: StageConfig(**v) for k, v in user_config['stages'].items()}}
        else:
            stages = base.stages
        # default_rules
        default_rules = user_config.get('default_rules', base.default_rules)
        # default_variables
        default_variables = {**base.default_variables, **user_config.get('default_variables', {})}
        # templates
        templates = base.templates
        if 'templates' in user_config:
            templates = TemplatesConfig(**{**base.templates.__dict__, **user_config['templates']})
        # output
        output = base.output
        if 'output' in user_config:
            output = OutputConfig(**{**base.output.__dict__, **user_config['output']})
        # supported_stages
        supported_stages = user_config.get('supported_stages', base.supported_stages)
        # file_search
        file_search = base.file_search
        if 'file_search' in user_config:
            file_search = FileSearchConfig(**{**base.file_search.__dict__, **user_config['file_search']})
        return DefaultConfig(
            stages=stages,
            default_rules=default_rules,
            default_variables=default_variables,
            templates=templates,
            output=output,
            supported_stages=supported_stages,
            file_search=file_search,
        )

    def get_config(self, user_config_path: Optional[str] = None) -> DefaultConfig:
        user_config = self.load_user_config(user_config_path)
        return self.merge_configs(user_config)

    def get_stage_config(self, stage: str, config: DefaultConfig) -> StageConfig:
        return config.stages.get(stage, None)

    def get_supported_stages(self, config: DefaultConfig) -> list:
        return config.supported_stages

    def get_template_path(self, template_name: str, config: DefaultConfig) -> Path:
        templates_dir = Path(__file__).parent.parent / "templates"
        template_file = getattr(config.templates, template_name, f"{template_name}.j2")
        return templates_dir / template_file