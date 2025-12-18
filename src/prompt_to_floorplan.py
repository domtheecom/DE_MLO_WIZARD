#!/usr/bin/env python3
"""Prompt to deterministic floorplan generator.

This script uses template-driven heuristics to transform a natural language prompt
into a structured JSON file describing a basic multi-floor blockout. No external
LLM calls are performed so it is fully offline and reproducible.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_WALL_THICKNESS = 0.2
DEFAULT_FLOOR_HEIGHT = 3.2


@dataclass
class Room:
    name: str
    width: float
    depth: float
    height: float
    floor: int
    type: str = "generic"


@dataclass
class Door:
    name: str
    width: float
    type: str
    floor: int


@dataclass
class Floorplan:
    metadata: Dict[str, str]
    rooms: List[Room]
    corridors: List[Dict[str, float]]
    doors: List[Door]
    stairs: List[Dict[str, float]]
    settings: Dict[str, float]


TEMPLATES = {
    "fire station": {
        "rooms": [
            ("Apparatus Bay", 14.0, 12.0, "bay"),
            ("Watch Office", 5.0, 4.0, "office"),
            ("Dormitory", 8.0, 6.0, "sleep"),
            ("Kitchen", 6.0, 5.0, "kitchen"),
            ("Dayroom", 7.0, 6.0, "lounge"),
            ("Gear Room", 6.0, 5.0, "storage"),
        ],
        "hallway_width": 3.0,
        "bay_door_width": 4.2,
    },
    "police station": {
        "rooms": [
            ("Lobby", 6.0, 5.0, "lobby"),
            ("Front Desk", 5.0, 4.0, "office"),
            ("Holding Cells", 8.0, 6.0, "cell"),
            ("Interview", 4.0, 4.0, "office"),
            ("Briefing Room", 7.0, 6.0, "meeting"),
            ("Evidence", 5.0, 4.0, "storage"),
        ],
        "hallway_width": 2.6,
        "bay_door_width": 0.0,
    },
    "hospital": {
        "rooms": [
            ("ER", 10.0, 8.0, "medical"),
            ("Waiting", 6.0, 5.0, "lobby"),
            ("Nurses", 5.0, 4.0, "office"),
            ("Exam", 4.0, 4.0, "medical"),
            ("Surgery", 7.0, 6.0, "medical"),
        ],
        "hallway_width": 2.8,
        "bay_door_width": 0.0,
    },
    "nightclub": {
        "rooms": [
            ("Main Floor", 12.0, 10.0, "lounge"),
            ("Bar", 8.0, 4.0, "bar"),
            ("DJ Booth", 3.0, 3.0, "stage"),
            ("Storage", 4.0, 4.0, "storage"),
            ("Office", 4.0, 4.0, "office"),
        ],
        "hallway_width": 2.4,
        "bay_door_width": 0.0,
    },
    "warehouse": {
        "rooms": [
            ("Warehouse Floor", 16.0, 12.0, "storage"),
            ("Office", 5.0, 4.0, "office"),
            ("Loading Dock", 8.0, 6.0, "dock"),
        ],
        "hallway_width": 2.5,
        "bay_door_width": 4.0,
    },
    "generic": {
        "rooms": [
            ("Lobby", 5.0, 4.0, "lobby"),
            ("Open Office", 10.0, 8.0, "office"),
            ("Conference", 6.0, 5.0, "meeting"),
        ],
        "hallway_width": 2.4,
        "bay_door_width": 0.0,
    },
}


BUILDING_KEYWORDS = {
    "fire": "fire station",
    "firehouse": "fire station",
    "station": "fire station",
    "police": "police station",
    "hospital": "hospital",
    "clinic": "hospital",
    "nightclub": "nightclub",
    "club": "nightclub",
    "warehouse": "warehouse",
}


def detect_template(prompt: str) -> str:
    lowered = prompt.lower()
    for keyword, template in BUILDING_KEYWORDS.items():
        if keyword in lowered:
            return template
    return "generic"


def build_rooms(template_key: str, floors: int) -> List[Room]:
    template = TEMPLATES.get(template_key, TEMPLATES["generic"])
    rooms: List[Room] = []
    for floor in range(floors):
        for name, width, depth, rtype in template["rooms"]:
            rooms.append(Room(name=name, width=width, depth=depth, height=DEFAULT_FLOOR_HEIGHT, floor=floor, type=rtype))
    return rooms


def default_corridors(floors: int, hallway_width: float) -> List[Dict[str, float]]:
    return [
        {
            "name": f"Corridor_{i+1}",
            "width": hallway_width,
            "length": 12.0,
            "floor": i,
        }
        for i in range(floors)
    ]


def default_stairs(floors: int, floor_height: float) -> List[Dict[str, float]]:
    return [
        {
            "name": f"Stair_{i}_{i+1}",
            "from_floor": i,
            "to_floor": i + 1,
            "rise": floor_height,
        }
        for i in range(max(floors - 1, 0))
    ]


def default_doors(template_key: str, floors: int, bay_width: float) -> List[Door]:
    doors: List[Door] = []
    for floor in range(floors):
        doors.append(Door(name=f"Entry_{floor}", width=1.0, type="single", floor=floor))
        doors.append(Door(name=f"Double_{floor}", width=1.8, type="double", floor=floor))
        if bay_width > 0:
            doors.append(Door(name=f"Bay_{floor}", width=bay_width, type="bay", floor=floor))
    return doors


def parse_prompt(prompt: str, floors: int, place: str) -> Floorplan:
    template_key = detect_template(prompt)
    template = TEMPLATES.get(template_key, TEMPLATES["generic"])
    rooms = build_rooms(template_key, floors)
    corridors = default_corridors(floors, template["hallway_width"])
    stairs = default_stairs(floors, DEFAULT_FLOOR_HEIGHT)
    doors = default_doors(template_key, floors, template["bay_door_width"])
    metadata = {
        "source_prompt": prompt,
        "inferred_template": template_key,
        "place": place,
        "floors": str(floors),
    }
    settings = {
        "wall_thickness": DEFAULT_WALL_THICKNESS,
        "floor_height": DEFAULT_FLOOR_HEIGHT,
        "hallway_width": template["hallway_width"],
    }
    return Floorplan(metadata=metadata, rooms=rooms, corridors=corridors, doors=doors, stairs=stairs, settings=settings)


def write_plan_markdown(plan: Floorplan, path: Path) -> None:
    lines = ["# Generated PLAN", "", f"Template: {plan.metadata['inferred_template']}", f"Floors: {plan.metadata['floors']}", ""]
    lines.append("## Rooms")
    for room in plan.rooms:
        lines.append(f"- Floor {room.floor}: {room.name} ({room.width}m x {room.depth}m, {room.type})")
    lines.append("")
    lines.append("## Doors")
    for door in plan.doors:
        lines.append(f"- Floor {door.floor}: {door.name} ({door.type}, width {door.width}m)")
    lines.append("")
    lines.append("## Corridors")
    for cor in plan.corridors:
        lines.append(f"- Floor {cor['floor']}: {cor['name']} (width {cor['width']}m, length {cor['length']}m)")
    lines.append("")
    lines.append("## Stairs")
    for stair in plan.stairs:
        lines.append(f"- {stair['name']} from floor {stair['from_floor']} to {stair['to_floor']} rise {stair['rise']}m")
    path.write_text("\n".join(lines), encoding="utf-8")


def serialize_plan(plan: Floorplan) -> Dict[str, object]:
    return {
        "metadata": plan.metadata,
        "rooms": [asdict(room) for room in plan.rooms],
        "corridors": plan.corridors,
        "doors": [asdict(door) for door in plan.doors],
        "stairs": plan.stairs,
        "settings": plan.settings,
    }


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Convert prompt to floorplan JSON")
    parser.add_argument("--prompt", required=True, help="Natural language building description")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--place", default="", help="Placement hint")
    parser.add_argument("--floors", type=int, default=1, help="Number of floors")
    parser.add_argument("--plan-doc", default=None, help="Optional PLAN.md output")
    args = parser.parse_args(argv)

    plan = parse_prompt(args.prompt, args.floors, args.place)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(serialize_plan(plan), indent=2), encoding="utf-8")

    if args.plan_doc:
        write_plan_markdown(plan, Path(args.plan_doc))

    print(f"Wrote floorplan to {out_path}")


if __name__ == "__main__":
    main()
