"""Model sources: where the C4 model comes from (IcePanel, legacy ArchiMate)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from archi_c4_score.archimate_xml_parser import ArchimateXMLParser
from archi_c4_score.c4_converter import C4ConversionResult, C4Converter


@dataclass
class ModelVersion:
    """A named version of the model (IcePanel version, or a git commit for ArchiMate)."""

    id: str
    name: str
    created_at: str = ""


class ModelSource(Protocol):
    """A source of C4 models. Scoring only depends on this interface."""

    def load(self, version_id: str = "latest") -> C4ConversionResult: ...

    def list_versions(self) -> list[ModelVersion]: ...


class ArchimateModelSource:
    """Legacy read-only source: a local .archimate file (ADR 0030)."""

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = Path(model_path)

    def load(self, version_id: str = "latest") -> C4ConversionResult:
        model = ArchimateXMLParser().parse_to_model(self.model_path)
        return C4Converter().convert_model(model)

    def list_versions(self) -> list[ModelVersion]:
        return [ModelVersion(id="latest", name=self.model_path.name)]

