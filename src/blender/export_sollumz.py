<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
import argparse
import sys
from pathlib import Path

import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

import utils_sollumz


def log(msg, log_file):
    print(msg)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def run_export(mode: str, out_dir: Path, resource_name: str, log_file: str):
    if not utils_sollumz.is_sollumz_loaded():
        log("Sollumz not loaded; cannot export.", log_file)
        return False

    stream = out_dir / "fivem_resource" / resource_name / "stream"
    stream.mkdir(parents=True, exist_ok=True)

    utils_sollumz.select_geo()
    selected = list(bpy.context.selected_objects)
    if not selected:
        log("No GEO objects selected for export.", log_file)
    for obj in selected:
        bpy.context.view_layer.objects.active = obj
        utils_sollumz.ensure_material(obj)

    export_op = utils_sollumz.find_op(["sollumz.export_assets"])
    if not export_op:
        log("Export operator missing.", log_file)
        return False

    try:
        export_op(directory=str(stream))
    except Exception as exc:
        log(f"Export error (directory): {exc}", log_file)
        try:
            export_op(filepath=str(stream))
        except Exception as nested:
            log(f"Export error (filepath): {nested}", log_file)

    # copy any generated files from cwd into stream for safety
    for ext in (".ydr", ".ydr.xml", ".ybn", ".ytyp"):
        for obj in Path.cwd().glob(f"*{ext}"):
            target = stream / obj.name
            if not target.exists():
                target.write_bytes(obj.read_bytes())

    ydr = list(stream.glob("*.ydr"))
    xml = list(stream.glob("*.ydr.xml"))
    if ydr:
        log("Binary YDR exports found.", log_file)
        return True
    if xml:
        log("XML export present. Run FinalExport to compile binaries.", log_file)
    else:
        log("No exports produced.", log_file)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", default="headless_xml")
    parser.add_argument("--resource-name", required=True)
    parser.add_argument("--log")
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args()
    run_export(args.mode, Path(args.output), args.resource_name, args.log)
=======
#!/usr/bin/env python3
"""Discover Sollumz operators and export blockout assets.

This script intentionally discovers operators dynamically to avoid hardcoding names.
If export operators are missing, it prints a guided set of manual steps.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import bpy

KEYWORDS = ["sollum", "sollumz", "ydr", "ybn", "ytyp", "export", "ymap"]


def list_matching_ops() -> Dict[str, bpy.types.Operator]:
    matches: Dict[str, bpy.types.Operator] = {}
    for op_id in dir(bpy.ops):
        if any(key in op_id for key in KEYWORDS):
            ops_sub = getattr(bpy.ops, op_id)
            for sub_id in dir(ops_sub):
                full_id = f"{op_id}.{sub_id}"
                if any(key in full_id for key in KEYWORDS):
                    matches[full_id] = getattr(ops_sub, sub_id)
    return matches


def choose_exports(matches: Dict[str, bpy.types.Operator]) -> Dict[str, str]:
    chosen: Dict[str, str] = {}
    for fmt in ("ytyp", "ydr", "ybn", "xml"):
        for op in matches:
            if fmt in op:
                chosen[fmt] = op
                break
    return chosen


def export_with_operator(op_path: str, output_dir: Path) -> None:
    print(f"Attempting export with operator: {op_path}")
    result = bpy.ops.__getattribute__(op_path.split(".")[0]).__getattribute__(op_path.split(".")[1])(filepath=str(output_dir))
    print(f"Result: {result}")


def manual_export_instructions() -> None:
    print("\nManual Sollumz export steps:")
    print("1. Open the saved blockout .blend file in Blender.")
    print("2. File > Export and look for Sollumz YDR/YBN/YTYP or XML export entries.")
    print("3. Export to the output folder's fivem_resource/stream directory.")
    print("4. Return to PowerShell and run mlo.ps1 with -SkipBlender to reuse the blend.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    matches = list_matching_ops()
    print("Discovered operators:")
    for op in matches:
        print(f" - {op}")

    chosen = choose_exports(matches)
    if not chosen:
        print("No Sollumz export operators detected. Export manually.")
        manual_export_instructions()
        return

    for fmt, op in chosen.items():
        try:
            export_with_operator(op, output_dir / "fivem_resource" / "stream")
        except Exception as exc:  # noqa: BLE001
            print(f"Failed export via {op}: {exc}")

    print("Exports attempted. Verify files in output directory. If missing, use manual steps above.")
>>>>>>> main


if __name__ == "__main__":
    main()
