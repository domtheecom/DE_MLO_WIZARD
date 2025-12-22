import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict


def _add_text(parent, tag, text):
    element = ET.SubElement(parent, tag)
    element.text = text
    return element


def _vector_to_text(vec: List[float]) -> str:
    return f"{vec[0]:.3f}, {vec[1]:.3f}, {vec[2]:.3f}"


def _add_entity(entities, archetype: str, position, rotation=None):
    if rotation is None:
        rotation = [0.0, 0.0, 0.0]
    item = ET.SubElement(entities, "Item", {"type": "CEntityDef"})
    _add_text(item, "archetypeName", archetype)
    _add_text(item, "position", _vector_to_text(position))
    _add_text(item, "rotation", _vector_to_text(rotation))
    _add_text(item, "scale", "1.000, 1.000, 1.000")
    _add_text(item, "flags", "0")
    _add_text(item, "guid", str(uuid.uuid4()))


def build_ymap(layout: dict, props: List[Dict]) -> str:
    root = ET.Element("CMapData")
    _add_text(root, "name", "de_scripts_mlo_generated")
    _add_text(root, "parent", "")
    _add_text(root, "flags", "0")
    entities = ET.SubElement(root, "entities")

    for module in layout.get("modules", []):
        _add_entity(
            entities,
            module["archetype"],
            module["position"],
            module.get("rotation", [0.0, 0.0, 0.0]),
        )

    for prop in props:
        _add_entity(entities, prop["archetype"], prop["position"], prop["rotation"])

    rough = ET.tostring(root, encoding="utf-8")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


__all__ = ["build_ymap"]
