"""
Модуль для загрузки и обработки конфигурационных файлов.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List


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
        "elab": StageConfig(
            tags=["soc-fpga-elab"], make_target="elab", description="FPGA Elaboration"
        ),
        "synth": StageConfig(
            tags=["soc-fpga-synth"], make_target="synth", description="FPGA Synthesis"
        ),
        "bitstream": StageConfig(
            tags=["soc-fpga-synth"],
            make_target="bitstream",
            description="FPGA Bitstream Generation",
        ),
    },
    default_rules=[{"when": "always"}],
    default_variables={},
    templates=TemplatesConfig(pipeline="pipeline.j2", job="job.j2"),
    output=OutputConfig(indent=2, default_filename="generated_pipeline.yml"),
    supported_stages=["elab", "synth", "bitstream"],
    file_search=FileSearchConfig(fpga_dir="fpga", config_filename="fpga-builds.yaml"),
)


class ConfigLoader:
    """Класс для загрузки конфигурационных файлов."""

    def __init__(self):
        self.default_config = DEFAULT_CONFIG

    def get_config(self) -> DefaultConfig:
        return self.default_config

    def get_stage_config(self, stage: str, config: DefaultConfig) -> StageConfig:
        return config.stages.get(stage, None)

    def get_supported_stages(self, config: DefaultConfig) -> list:
        return config.supported_stages

    def get_template_path(self, template_name: str, config: DefaultConfig) -> Path:
        templates_dir = Path(__file__).parent.parent / "templates"
        template_file = getattr(config.templates, template_name, f"{template_name}.j2")
        return templates_dir / template_file
