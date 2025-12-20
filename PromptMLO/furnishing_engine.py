import json
import os
from typing import Dict, List


def _load_props() -> Dict[str, List[Dict]]:
    path = os.path.join(os.path.dirname(__file__), "assets", "props.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_furnishings(layout: Dict) -> List[Dict]:
    props = _load_props()
    furnishings = []
    for module in layout["modules"]:
        room_type = module["room_type"]
        if room_type not in props:
            continue
        for item in props[room_type]:
            furnishings.append(
                {
                    "archetype": item["archetype"],
                    "position": {
                        "x": module["position"]["x"] + item["offset"]["x"],
                        "y": module["position"]["y"] + item["offset"]["y"],
                        "z": module["position"]["z"] + item["offset"]["z"],
                    },
                    "rotation": item.get("rotation", {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}),
                    "room": module["name"],
                }
            )
    return furnishings
