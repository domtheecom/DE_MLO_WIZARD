from typing import Dict, List


def build_portals(layout: Dict) -> List[Dict]:
    modules = [module for module in layout["modules"] if module["room_type"] not in {"shell"}]
    portals = []
    for index in range(len(modules) - 1):
        portals.append(
            {
                "from": modules[index]["name"],
                "to": modules[index + 1]["name"],
                "type": "doorway",
            }
        )
    return portals
