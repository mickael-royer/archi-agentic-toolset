"""ArchiMate model importer for native format (model.archimate).

Downloads model.archimate file directly from raw GitHub URL.
"""

import logging
import re
import urllib.request
from dataclasses import dataclass, field
from typing import Generator
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

ARCHIMATE_NS = {"archi": "http://www.archimatetool.com/archimate"}

ARCHIMATE_NS = {"archi": "http://www.archimatetool.com/archimate"}

ELEMENT_TYPE_MAP = {
    "BusinessActor": "BusinessActor",
    "BusinessRole": "BusinessRole",
    "BusinessProcess": "BusinessProcess",
    "BusinessFunction": "BusinessFunction",
    "BusinessObject": "BusinessObject",
    "ApplicationComponent": "ApplicationComponent",
    "ApplicationFunction": "ApplicationFunction",
    "ApplicationService": "ApplicationService",
    "ApplicationInterface": "ApplicationInterface",
    "ApplicationInteraction": "ApplicationInteraction",
    "DataObject": "DataObject",
    "TechnologyNode": "TechnologyNode",
    "TechnologyService": "TechnologyService",
    "TechnologyInterface": "TechnologyInterface",
    "Artifact": "Artifact",
    "SystemSoftware": "SystemSoftware",
    "Device": "Device",
    "Network": "Network",
    "CommunicationNetwork": "CommunicationNetwork",
    "Location": "Location",
    "Actor": "Actor",
    "Person": "Person",
    "WorkPackage": "WorkPackage",
    "Deliverable": "Deliverable",
    "Plateau": "Plateau",
    "Gap": "Gap",
    "Goal": "Goal",
    "Metric": "Metric",
    "Value": "Value",
    "Driver": "Driver",
    "Assessment": "Assessment",
    "Principle": "Principle",
    "Constraint": "Constraint",
    "Meaning": "Meaning",
    "Quality": "Quality",
    "Format": "Format",
}

RELATIONSHIP_TYPE_MAP = {
    "AccessRelationship": "Access",
    "AggregationRelationship": "Aggregation",
    "AssignmentRelationship": "Assignment",
    "AssociationRelationship": "Association",
    "CompositionRelationship": "Composition",
    "FlowRelationship": "Flow",
    "InfluenceRelationship": "Influence",
    "RealisationRelationship": "Realisation",
    "ServingRelationship": "Serving",
    "SpecialisationRelationship": "Specialisation",
    "TriggeringRelationship": "Triggering",
    "UsedByRelationship": "UsedBy",
}


@dataclass
class ArchiElement:
    """Archimate element parsed from model."""

    id: str
    name: str
    element_type: str
    documentation: str = ""
    properties: dict = field(default_factory=dict)


@dataclass
class ArchiRelationship:
    """Archimate relationship parsed from model."""

    id: str
    relationship_type: str
    source_id: str
    target_id: str
    properties: dict = field(default_factory=dict)


@dataclass
class ParsedModel:
    """Parsed Archi model."""

    elements: list[ArchiElement] = field(default_factory=list)
    relationships: list[ArchiRelationship] = field(default_factory=list)
    commit: str = ""


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from GitHub URL."""
    url = (
        url.rstrip("/")
        .replace("https://", "")
        .replace("http://", "")
        .replace("github.com/", "github.com:")
    )
    match = re.match(r"github\.com[/:]([^/]+)/([^/.]+)", url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return match.group(1), match.group(2)


def parse_model_archimate(
    xml_content: str,
) -> Generator[tuple[ArchiElement | ArchiRelationship, str], None, None]:
    """Parse model.archimate format (Archi native format).

    This format uses nested folders with xsi:type elements.
    """

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.warning(f"XML parse error: {e}")
        return

    def process_element(elem: ET.Element):
        """Recursively process elements in folders."""
        tag = elem.tag.replace("{http://www.archimatetool.com/archimate}", "")

        if tag == "element":
            xsi_type = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
            if xsi_type.startswith("archimate:"):
                element_type = xsi_type.replace("archimate:", "")

                if element_type in RELATIONSHIP_TYPE_MAP:
                    rel_type_mapped = RELATIONSHIP_TYPE_MAP.get(element_type, element_type)
                    yield (
                        ArchiRelationship(
                            id=elem.get("id", ""),
                            relationship_type=rel_type_mapped,
                            source_id=elem.get("source", ""),
                            target_id=elem.get("target", ""),
                            properties={},
                        ),
                        "relationship",
                    )
                elif element_type in ELEMENT_TYPE_MAP:
                    props = {}
                    for prop in elem.findall("property"):
                        key = prop.get("key", "")
                        value = prop.get("value", "")
                        if key and value:
                            props[key] = value

                    doc = ""
                    doc_elem = elem.find("documentation")
                    if doc_elem is not None:
                        doc = doc_elem.text or ""

                    yield (
                        ArchiElement(
                            id=elem.get("id", ""),
                            name=elem.get("name", ""),
                            element_type=ELEMENT_TYPE_MAP.get(element_type, element_type),
                            documentation=doc,
                            properties=props,
                        ),
                        "element",
                    )

        elif tag == "folder":
            for child in elem:
                yield from process_element(child)

    for child in root:
        yield from process_element(child)


def import_from_url(model_url: str) -> ParsedModel:
    """Import Archi model from raw GitHub URL (model.archimate file).

    Args:
        model_url: Direct URL to model.archimate file, e.g.,
            https://raw.githubusercontent.com/mickael-royer/archimate-ear/main/model.archimate
    """
    logger.info(f"Fetching model from: {model_url}")

    model = ParsedModel()

    try:
        with urllib.request.urlopen(model_url, timeout=30) as response:
            xml_content = response.read().decode("utf-8")

        for item, item_type in parse_model_archimate(xml_content):
            if item_type == "element":
                model.elements.append(item)
            else:
                model.relationships.append(item)

        logger.info(
            f"Parsed: {len(model.elements)} elements, {len(model.relationships)} relationships"
        )
    except Exception as e:
        logger.error(f"Failed to fetch model: {e}")

    return model
