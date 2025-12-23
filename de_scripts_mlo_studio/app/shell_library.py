from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_EXTENSIONS = {".ydr", ".ybn", ".ytyp", ".ytd"}


@dataclass
class ShellMetadata:
    shell_name: str
    tags: list[str]
    floors: int
    bay_count: int
    footprint: dict[str, float]
    recommended_props: list[str]
    archetype_name: str
    preview_image: str


class ShellLibrary:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.assets_catalog = base_dir / "assets" / "shell_library.json"
        self.user_data_dir = base_dir / "user_data" / "shells"
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

    def load_shells(self) -> list[dict[str, Any]]:
        shells: list[dict[str, Any]] = []
        if self.assets_catalog.exists():
            with self.assets_catalog.open("r", encoding="utf-8") as handle:
                shells.extend(json.load(handle).get("shells", []))

        for metadata_file in self.user_data_dir.glob("*/metadata.json"):
            with metadata_file.open("r", encoding="utf-8") as handle:
                shells.append(json.load(handle))

        return shells

    def import_shell_folder(self, source_dir: Path, shell_name: str) -> ShellMetadata:
        if not source_dir.exists():
            raise FileNotFoundError("Selected shell folder does not exist.")

        destination = self.user_data_dir / shell_name
        destination.mkdir(parents=True, exist_ok=True)

        copied = []
        for item in source_dir.iterdir():
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                shutil.copy2(item, destination / item.name)
                copied.append(item.name)

        if not copied:
            raise ValueError("No .ydr/.ybn/.ytyp files found in the selected folder.")

        metadata = ShellMetadata(
            shell_name=shell_name,
            tags=[],
            floors=1,
            bay_count=0,
            footprint={"width": 20.0, "depth": 20.0, "height": 10.0},
            recommended_props=[],
            archetype_name=f"{shell_name}_shell",
            preview_image="",
        )

        metadata_file = destination / "metadata.json"
        with metadata_file.open("w", encoding="utf-8") as handle:
            json.dump(metadata.__dict__, handle, indent=2)

        return metadata
