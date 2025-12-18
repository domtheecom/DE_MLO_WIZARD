#!/usr/bin/env python3
"""Blender headless blockout builder.

Executed via `blender -b -P build_from_floorplan.py -- --floorplan floorplan.json --output outdir`.
Creates simple rectangular rooms, walls, ceilings, corridors, and stair placeholders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import bpy

COLLECTIONS = {
    "GEO": None,
    "COLLISION": None,
    "HELPERS": None,
}


def ensure_collections() -> None:
    for name in COLLECTIONS:
        if name in bpy.data.collections:
            COLLECTIONS[name] = bpy.data.collections[name]
        else:
            COLLECTIONS[name] = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(COLLECTIONS[name])


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for collection in list(bpy.data.collections):
        if collection.users == 0 and collection.name not in COLLECTIONS:
            bpy.data.collections.remove(collection)


def create_box(width: float, depth: float, height: float, name: str, collection) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (width / 2, depth / 2, height / 2)
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj


def add_room(room: Dict[str, object]) -> None:
    obj = create_box(room["width"], room["depth"], room["height"], f"ROOM_{room['name'].replace(' ', '_')}_{room['floor']}", COLLECTIONS["GEO"])
    obj.location = (0, 0, room["floor"] * room["height"])

    wall_thickness = room.get("wall_thickness", 0.2)
    wall_height = room["height"]
    for idx, (dx, dy, w, d) in enumerate([
        (room["width"] / 2 + wall_thickness / 2, 0, wall_thickness, room["depth"] + wall_thickness * 2),
        (-room["width"] / 2 - wall_thickness / 2, 0, wall_thickness, room["depth"] + wall_thickness * 2),
        (0, room["depth"] / 2 + wall_thickness / 2, room["width"], wall_thickness),
        (0, -room["depth"] / 2 - wall_thickness / 2, room["width"], wall_thickness),
    ]):
        wall = create_box(w, d, wall_height, f"WALL_{room['name'].replace(' ', '_')}_{room['floor']}_{idx}", COLLECTIONS["GEO"])
        wall.location = (dx, dy, room["floor"] * room["height"])

    ceiling = create_box(room["width"], room["depth"], 0.05, f"CEIL_{room['name'].replace(' ', '_')}_{room['floor']}", COLLECTIONS["GEO"])
    ceiling.location = (0, 0, room["floor"] * room["height"] + room["height"])


def add_corridor(corridor: Dict[str, object], height: float) -> None:
    length = corridor.get("length", 12.0)
    obj = create_box(corridor["width"], length, height, f"CORRIDOR_{corridor['name']}_{corridor['floor']}", COLLECTIONS["GEO"])
    obj.location = (0, 0, corridor["floor"] * height)


def add_stairs(stair: Dict[str, object], height: float) -> None:
    step_height = 0.2
    steps = int(height / step_height)
    for i in range(steps):
        step = create_box(1.2, 0.3, step_height, f"STAIR_{stair['name']}_{i}", COLLECTIONS["GEO"])
        step.location = (0, i * 0.28, stair["from_floor"] * height + i * step_height)


def add_helper_origin() -> None:
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    empty = bpy.context.active_object
    empty.name = "HELPER_ORIGIN"
    COLLECTIONS["HELPERS"].objects.link(empty)
    bpy.context.scene.collection.objects.unlink(empty)


def save_blend(path: Path) -> None:
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def build_from_plan(plan_path: Path, output_dir: Path, blend_path: Path) -> None:
    plan = json.loads(plan_path.read_text())
    clear_scene()
    ensure_collections()

    for room in plan.get("rooms", []):
        room["wall_thickness"] = plan.get("settings", {}).get("wall_thickness", 0.2)
        add_room(room)

    hallway_height = plan.get("settings", {}).get("floor_height", 3.2)
    for corridor in plan.get("corridors", []):
        add_corridor(corridor, hallway_height)

    for stair in plan.get("stairs", []):
        add_stairs(stair, hallway_height)

    add_helper_origin()
    output_dir.mkdir(parents=True, exist_ok=True)
    save_blend(blend_path)
    print(f"Saved blockout blend at {blend_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--floorplan", required=True, help="Floorplan JSON path")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--blend", required=True, help="Blend file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_from_plan(Path(args.floorplan), Path(args.output), Path(args.blend))


if __name__ == "__main__":
    main()
