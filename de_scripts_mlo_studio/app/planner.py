from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .prompt_parser import ParsedPrompt


@dataclass
class ShellChoice:
    shell_name: str
    archetype_name: str
    footprint: dict[str, float]
    floors: int
    bay_count: int


@dataclass
class Placement:
    archetypeName: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]
    scaleXY: float
    scaleZ: float


@dataclass
class PlanResult:
    shell: ShellChoice
    placements: list[Placement]
    modules: list[str]


class PlannerError(Exception):
    pass


def _load_catalog(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def choose_shell(
    parsed: ParsedPrompt,
    shell_catalog: list[dict[str, Any]],
    manual_shell: str | None = None,
) -> ShellChoice:
    if manual_shell and manual_shell != "Auto":
        for shell in shell_catalog:
            if shell["shell_name"] == manual_shell:
                return ShellChoice(
                    shell_name=shell["shell_name"],
                    archetype_name=shell["archetype_name"],
                    footprint=shell["footprint"],
                    floors=shell.get("floors", 1),
                    bay_count=shell.get("bay_count", 0),
                )
        raise PlannerError(f"Shell '{manual_shell}' not found in library.")

    desired_tags = {parsed.building_type, *parsed.key_rooms}
    scored = []
    for shell in shell_catalog:
        tags = set(shell.get("tags", []))
        score = len(desired_tags.intersection(tags))
        score += 1 if shell.get("floors", 1) >= parsed.floors else 0
        score += 1 if shell.get("bay_count", 0) >= parsed.bays else 0
        scored.append((score, shell))

    if not scored:
        raise PlannerError("No shells available in the library.")

    scored.sort(key=lambda item: item[0], reverse=True)
    chosen = scored[0][1]
    return ShellChoice(
        shell_name=chosen["shell_name"],
        archetype_name=chosen["archetype_name"],
        footprint=chosen["footprint"],
        floors=chosen.get("floors", 1),
        bay_count=chosen.get("bay_count", 0),
    )


def plan_layout(
    parsed: ParsedPrompt,
    shell: ShellChoice,
    props_catalog_path: Path,
) -> PlanResult:
    props_catalog = _load_catalog(props_catalog_path)
    random_seed = abs(hash(parsed.raw_prompt)) % (2**32)
    rng = random.Random(random_seed)

    width = shell.footprint.get("width", 20.0)
    depth = shell.footprint.get("depth", 20.0)

    room_count = max(len(parsed.key_rooms), 1)
    grid_cols = max(1, int(room_count**0.5))
    grid_rows = max(1, (room_count + grid_cols - 1) // grid_cols)

    cell_w = width / grid_cols
    cell_d = depth / grid_rows

    placements: list[Placement] = []
    modules = []

    for idx, room in enumerate(parsed.key_rooms):
        room_props = props_catalog.get(room, [])
        if not room_props:
            continue

        col = idx % grid_cols
        row = idx // grid_cols
        origin_x = -width / 2 + (col + 0.5) * cell_w
        origin_y = -depth / 2 + (row + 0.5) * cell_d

        for prop in room_props:
            offset = prop.get("offset", [0.0, 0.0, 0.0])
            jitter = (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4))
            pos = (
                origin_x + offset[0] + jitter[0],
                origin_y + offset[1] + jitter[1],
                offset[2],
            )
            placements.append(
                Placement(
                    archetypeName=prop["archetypeName"],
                    position=pos,
                    rotation=(0.0, 0.0, 0.0, 1.0),
                    scaleXY=1.0,
                    scaleZ=1.0,
                )
            )

    for feature in parsed.exterior_features:
        modules.append(feature)
        exterior_props = props_catalog.get("exterior", [])
        anchor_x = width / 2 + 4.0
        anchor_y = depth / 2 + 4.0
        for prop in exterior_props:
            offset = prop.get("offset", [0.0, 0.0, 0.0])
            pos = (
                anchor_x + offset[0],
                anchor_y + offset[1],
                offset[2],
            )
            placements.append(
                Placement(
                    archetypeName=prop["archetypeName"],
                    position=pos,
                    rotation=(0.0, 0.0, 0.0, 1.0),
                    scaleXY=1.0,
                    scaleZ=1.0,
                )
            )

    return PlanResult(shell=shell, placements=placements, modules=modules)
