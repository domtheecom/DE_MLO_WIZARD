from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable

from .planner import Placement, PlanResult
from .ymap_export import write_ymap


def write_fxmanifest(resource_dir: Path, resource_name: str) -> None:
    manifest = (
        "fx_version 'cerulean'\n"
        "game 'gta5'\n"
        "this_is_a_map 'yes'\n\n"
        f"files {{ 'stream/{resource_name}_PLACEME.ymap' }}\n"
    )
    (resource_dir / "fxmanifest.lua").write_text(manifest, encoding="utf-8")


def write_build_spec(resource_dir: Path, spec: dict) -> None:
    data_dir = resource_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "build_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")


def write_placements(resource_dir: Path, placements: Iterable[Placement]) -> None:
    data_dir = resource_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "archetypeName": placement.archetypeName,
            "position": placement.position,
            "rotation": placement.rotation,
            "scaleXY": placement.scaleXY,
            "scaleZ": placement.scaleZ,
        }
        for placement in placements
    ]
    (data_dir / "placements.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def copy_shell_files(shell_folder: Path, stream_dir: Path) -> None:
    stream_dir.mkdir(parents=True, exist_ok=True)
    for item in shell_folder.iterdir():
        if item.is_file() and item.suffix.lower() in {".ydr", ".ybn", ".ytyp", ".ytd"}:
            shutil.copy2(item, stream_dir / item.name)


def export_resource(
    output_dir: Path,
    resource_name: str,
    plan: PlanResult,
    placements: list[Placement],
    anchor_archetype: str,
    copy_shell: bool,
    shell_folder: Path | None,
    codewalker_readme: str,
    build_spec: dict,
) -> Path:
    resource_dir = output_dir / resource_name
    stream_dir = resource_dir / "stream"
    preview_dir = resource_dir / "preview"

    resource_dir.mkdir(parents=True, exist_ok=True)
    stream_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    write_fxmanifest(resource_dir, resource_name)
    write_build_spec(resource_dir, build_spec)
    write_placements(resource_dir, placements)

    if copy_shell and shell_folder is not None:
        copy_shell_files(shell_folder, stream_dir)

    ymap_path = stream_dir / f"{resource_name}_PLACEME.ymap"
    write_ymap(ymap_path, placements, anchor_archetype)

    (resource_dir / "README_CODEWALKER.md").write_text(codewalker_readme, encoding="utf-8")

    return resource_dir
