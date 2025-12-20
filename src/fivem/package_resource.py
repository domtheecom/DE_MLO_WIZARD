<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
import argparse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from codewalker.placement_pack import build_docs

def write_fxmanifest(stream_dir: Path, resource: str):
    fx = stream_dir.parent / "fxmanifest.lua"
    fx.write_text(
        "\n".join(
            [
                "fx_version 'cerulean'",
                "game 'gta5'",
                f"this_is_a_map 'yes'",
                "files {\n    'stream/*'\n}",
                "data_file 'DLC_ITYP_REQUEST' 'stream/*.ytyp'",
            ]
        ),
        encoding="utf-8",
    )


def write_readme(out_dir: Path, resource: str, place: str):
    readme = out_dir / "README.txt"
    readme.write_text(
        "\n".join(
            [
                f"# {resource}",
                "1) Run .\\mlo.ps1 -Doctor",
                "2) Run build command",
                "3) If only XML exports: .\\mlo.ps1 -FinalExport -Out <path>",
                "4) Copy resource folder to server resources and start it.",
                "",
                f"Place: {place}",
            ]
        ),
        encoding="utf-8",
    )


def copy_docs(src_dir: Path, dest: Path):
    for name in ["floorplan.json", "PLAN.md", "props_manifest.json", "export_log.txt"]:
        path = src_dir / name
        if path.exists():
            (dest / name).write_bytes(path.read_bytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--resource-name", required=True)
    ap.add_argument("--place", default="")
    ap.add_argument("--coordsx", type=float, default=None)
    ap.add_argument("--coordsy", type=float, default=None)
    ap.add_argument("--coordsz", type=float, default=None)
    ap.add_argument("--heading", type=float, default=None)
    args = ap.parse_args()

    source = Path(args.source)
    resource_root = source / "fivem_resource" / args.resource_name
    stream_dir = resource_root / "stream"
    docs_dir = resource_root / "data"
    stream_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    write_fxmanifest(stream_dir, args.resource_name)
    write_readme(resource_root, args.resource_name, args.place)
    copy_docs(source, docs_dir)

    coords = None
    if args.coordsx is not None:
        coords = (args.coordsx, args.coordsy, args.coordsz, args.heading)
    build_docs(docs_dir, args.resource_name, coords)
=======
#!/usr/bin/env python3
"""Package exported assets into a FiveM-ready resource."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

FX_TEMPLATE = """fx_version 'cerulean'
game 'gta5'

this_is_a_map 'yes'

files {
    'stream/*.ytyp',
    'stream/*.ydr',
    'stream/*.ybn',
    'data/*.ymap',
    'data/*.xml'
}

data_file 'DLC_ITYP_REQUEST' 'stream/*.ytyp'
"""

README_TEMPLATE = """# FiveM Map Resource

Drop this folder into your server's `resources/` directory and add `ensure {name}` to `server.cfg`.

## Contents
- Streamed geometry (YDR/YBN/YTYP) under `stream/`.
- Optional placement/XML data under `data/`.
- `fxmanifest.lua` already configured as a map resource.

## Quick Test
1. Start your FiveM server with the resource ensured.
2. Use CodeWalker or in-game coordinates to teleport near the placement guide coordinates.
3. Use noclip to inspect interior alignment.

## Placement Helper
A `PLACEMENT.md` file provides suggested origin, rotation, and manual CodeWalker steps.
"""

PLACEMENT_TEMPLATE = """# Placement Helper

Suggested location: {place}
Suggested rotation: 0,0,0
Interior origin marker: at (0,0,0) relative to exported assets.

Manual CodeWalker steps (guided):
1. Open CodeWalker and load the GTA V map.
2. Import the XML from `data/` if generated, or use Sollumz-imported XMLs.
3. Create a new YMAP and position the MLO at your chosen coordinates.
4. Set the entity's rotation and ensure the interior origin lines up with the helper object.
5. Save the YMAP and export XML for future Blender imports.

Note: Headless CodeWalker automation is not guaranteed; follow the checklist above unless you enable your own API.
"""


def write_fxmanifest(path: Path) -> None:
    path.write_text(FX_TEMPLATE, encoding="utf-8")


def write_readme(path: Path, name: str) -> None:
    path.write_text(README_TEMPLATE.format(name=name), encoding="utf-8")


def write_placement(path: Path, place: str) -> None:
    path.write_text(PLACEMENT_TEMPLATE.format(place=place or "Sandy Shores"), encoding="utf-8")


def package_resource(source: Path, resource_name: str, place: str) -> Path:
    target = source / "fivem_resource" / resource_name
    stream_dir = target / "stream"
    data_dir = target / "data"
    stream_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    write_fxmanifest(target / "fxmanifest.lua")
    write_readme(target / "README.md", resource_name)
    write_placement(target / "PLACEMENT.md", place)

    plan_path = source / "floorplan.json"
    if plan_path.exists():
        (target / "PLAN.copy.json").write_text(plan_path.read_text(), encoding="utf-8")

    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Package FiveM map resource")
    parser.add_argument("--source", required=True, help="Build output directory")
    parser.add_argument("--resource-name", default="mlo_build", help="Resource name")
    parser.add_argument("--place", default="", help="Placement hint")
    args = parser.parse_args()

    resource_path = package_resource(Path(args.source), args.resource_name, args.place)
    print(f"Resource packaged at {resource_path}")
>>>>>>> main


if __name__ == "__main__":
    main()
