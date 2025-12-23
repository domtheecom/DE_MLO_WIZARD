from __future__ import annotations

import uuid
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .planner import Placement


def _calc_extents(placements: Iterable[Placement], padding: float = 6.0) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    xs = [p.position[0] for p in placements] or [0.0]
    ys = [p.position[1] for p in placements] or [0.0]
    zs = [p.position[2] for p in placements] or [0.0]
    min_ext = (min(xs) - padding, min(ys) - padding, min(zs) - padding)
    max_ext = (max(xs) + padding, max(ys) + padding, max(zs) + padding)
    return min_ext, max_ext


def _entity_item(placement: Placement, guid: str) -> ET.Element:
    item = ET.Element("Item", {"type": "CEntityDef"})
    ET.SubElement(item, "archetypeName").text = placement.archetypeName
    ET.SubElement(item, "flags").text = "0"
    ET.SubElement(item, "guid").text = guid
    ET.SubElement(item, "position", {"x": f"{placement.position[0]:.3f}", "y": f"{placement.position[1]:.3f}", "z": f"{placement.position[2]:.3f}"})
    ET.SubElement(item, "rotation", {"x": f"{placement.rotation[0]:.6f}", "y": f"{placement.rotation[1]:.6f}", "z": f"{placement.rotation[2]:.6f}", "w": f"{placement.rotation[3]:.6f}"})
    ET.SubElement(item, "scaleXY").text = f"{placement.scaleXY:.3f}"
    ET.SubElement(item, "scaleZ").text = f"{placement.scaleZ:.3f}"
    return item


def build_ymap(placements: list[Placement], anchor_archetype: str) -> ET.ElementTree:
    map_data = ET.Element("mapData")
    c_map_data = ET.SubElement(map_data, "CMapData")

    ET.SubElement(c_map_data, "name").text = "DE_SCRIPTS_MLO"
    ET.SubElement(c_map_data, "entities")

    anchor = Placement(
        archetypeName=anchor_archetype,
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0, 1.0),
        scaleXY=1.0,
        scaleZ=1.0,
    )
    entity_list = c_map_data.find("entities")
    assert entity_list is not None

    entity_list.append(_entity_item(anchor, str(uuid.uuid4())))
    for placement in placements:
        entity_list.append(_entity_item(placement, str(uuid.uuid4())))

    min_ext, max_ext = _calc_extents([anchor, *placements])
    ET.SubElement(c_map_data, "streamingExtentsMin", {
        "x": f"{min_ext[0]:.3f}",
        "y": f"{min_ext[1]:.3f}",
        "z": f"{min_ext[2]:.3f}",
    })
    ET.SubElement(c_map_data, "streamingExtentsMax", {
        "x": f"{max_ext[0]:.3f}",
        "y": f"{max_ext[1]:.3f}",
        "z": f"{max_ext[2]:.3f}",
    })
    ET.SubElement(c_map_data, "entitiesExtentsMin", {
        "x": f"{min_ext[0]:.3f}",
        "y": f"{min_ext[1]:.3f}",
        "z": f"{min_ext[2]:.3f}",
    })
    ET.SubElement(c_map_data, "entitiesExtentsMax", {
        "x": f"{max_ext[0]:.3f}",
        "y": f"{max_ext[1]:.3f}",
        "z": f"{max_ext[2]:.3f}",
    })

    return ET.ElementTree(map_data)


def write_ymap(path: Path, placements: list[Placement], anchor_archetype: str) -> None:
    tree = build_ymap(placements, anchor_archetype)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)
