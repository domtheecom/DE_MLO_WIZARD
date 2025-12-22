import json
import os
from typing import List, Dict


class PropsLibraryError(RuntimeError):
    pass


def load_props_library(path: str) -> dict:
    if not os.path.exists(path):
        raise PropsLibraryError(f"Props library not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise PropsLibraryError(f"Invalid props library JSON: {exc}") from exc


def build_furnishings(layout: dict, props_library_path: str) -> List[Dict]:
    props_library = load_props_library(props_library_path)
    props = []
    for module in layout.get("modules", []):
        kind = module["kind"]
        if kind not in props_library:
            continue
        for prop in props_library[kind]:
            position = [
                module["position"][0] + prop["offset"][0],
                module["position"][1] + prop["offset"][1],
                module["position"][2] + prop["offset"][2],
            ]
            props.append(
                {
                    "archetype": prop["archetype"],
                    "position": position,
                    "rotation": prop.get("rotation", [0.0, 0.0, 0.0]),
                }
            )
    return props


__all__ = ["build_furnishings", "load_props_library", "PropsLibraryError"]
