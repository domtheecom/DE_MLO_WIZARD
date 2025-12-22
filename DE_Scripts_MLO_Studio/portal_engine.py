from typing import List, Dict


def build_portals(layout: dict) -> List[Dict]:
    modules = layout.get("modules", [])
    portals = []
    for module in modules:
        if module["kind"] == "shell":
            portals.append(
                {
                    "from": "shell",
                    "to": "exterior",
                    "position": [0.0, -4.0, 0.0],
                }
            )
            break
    return portals


__all__ = ["build_portals"]
