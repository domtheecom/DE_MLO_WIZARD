import json
import os
from typing import List, Dict


class ModuleLibraryError(RuntimeError):
    pass


def load_module_library(path: str) -> dict:
    if not os.path.exists(path):
        raise ModuleLibraryError(f"Module library not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ModuleLibraryError(f"Invalid module library JSON: {exc}") from exc
    if "fire_station" not in data:
        raise ModuleLibraryError("Module library missing 'fire_station' section")
    return data


def _warn_archetype(archetype: str) -> List[str]:
    warnings = []
    lower = archetype.lower()
    if lower.startswith("v_") or "placeholder" in lower:
        warnings.append(
            f"Archetype '{archetype}' may be placeholder or missing in your pack."
        )
    return warnings


def build_layout(spec: dict, module_library_path: str) -> Dict:
    library = load_module_library(module_library_path)
    modules = []
    warnings: List[str] = []

    def add_module(kind: str, position: List[float], rotation=None):
        if rotation is None:
            rotation = [0.0, 0.0, 0.0]
        module = library[spec["type"]][kind]
        archetype = module["archetype"]
        warnings.extend(_warn_archetype(archetype))
        modules.append(
            {
                "kind": kind,
                "archetype": archetype,
                "position": position,
                "rotation": rotation,
                "size": module["size"],
            }
        )

    add_module("shell", [0.0, 0.0, 0.0])

    bay_count = spec.get("garage_bays", 0)
    bay_spacing = 10.0
    for index in range(bay_count):
        add_module("bay", [0.0, 12.0 + index * bay_spacing, 0.0])

    office_count = spec.get("offices", 0)
    office_spacing = 7.0
    for index in range(office_count):
        add_module("office", [-10.0, index * office_spacing, 0.0])

    if spec.get("floors", 1) >= 2:
        add_module("stairs", [4.0, -2.0, 0.0])
        dorm_count = spec.get("dorms", 0)
        dorm_spacing = 7.0
        for index in range(dorm_count):
            add_module("dorm", [-8.0, index * dorm_spacing, 4.0])

    layout = {
        "modules": modules,
        "warnings": warnings,
    }
    return layout


__all__ = ["build_layout", "load_module_library", "ModuleLibraryError"]
