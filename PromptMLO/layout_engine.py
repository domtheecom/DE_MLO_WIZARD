import json
import os
from typing import Dict, List


def _load_module_library() -> Dict[str, Dict]:
    path = os.path.join(os.path.dirname(__file__), "module_library.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_layout(parsed_prompt: Dict[str, int | str]) -> Dict:
    library = _load_module_library()
    building_type = parsed_prompt["building_type"]

    modules = []
    exterior = library["exterior_shells"].get(building_type, library["exterior_shells"]["fire station"])
    modules.append(
        {
            "name": "exterior_shell",
            "archetype": exterior["archetype"],
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
            "room_type": "shell",
            "size": exterior["size"],
        }
    )

    floor_height = library["defaults"]["floor_height"]
    spacing = library["defaults"]["module_spacing"]

    current_x = -spacing
    current_y = spacing

    for floor in range(parsed_prompt["floors"]):
        z = floor * floor_height
        if floor > 0:
            modules.append(
                {
                    "name": f"stairs_floor_{floor}",
                    "archetype": library["interior_modules"]["stairs"]["archetype"],
                    "position": {"x": 0.0, "y": -spacing, "z": z},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                    "room_type": "stairs",
                    "size": library["interior_modules"]["stairs"]["size"],
                }
            )

        for office_index in range(parsed_prompt["offices"]):
            modules.append(
                {
                    "name": f"office_{floor}_{office_index}",
                    "archetype": library["interior_modules"]["office"]["archetype"],
                    "position": {"x": current_x, "y": current_y, "z": z},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                    "room_type": "office",
                    "size": library["interior_modules"]["office"]["size"],
                }
            )
            current_x += spacing

        for dorm_index in range(parsed_prompt["dorms"]):
            modules.append(
                {
                    "name": f"dorm_{floor}_{dorm_index}",
                    "archetype": library["interior_modules"]["dorm"]["archetype"],
                    "position": {"x": current_x, "y": current_y, "z": z},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                    "room_type": "dorm",
                    "size": library["interior_modules"]["dorm"]["size"],
                }
            )
            current_x += spacing

        current_x = -spacing
        current_y -= spacing

    for bay_index in range(parsed_prompt["garage_bays"]):
        modules.append(
            {
                "name": f"garage_{bay_index}",
                "archetype": library["interior_modules"]["garage_bay"]["archetype"],
                "position": {"x": bay_index * spacing, "y": spacing * 2, "z": 0.0},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                "room_type": "garage",
                "size": library["interior_modules"]["garage_bay"]["size"],
            }
        )

    return {
        "building_type": building_type,
        "modules": modules,
    }
