import argparse
import bpy
import os
from pathlib import Path
from . import utils_sollumz


def log(msg, log_file):
    print(msg)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def run_export(mode: str, out_dir: Path, resource_name: str, log_file: str):
    if not utils_sollumz.is_sollumz_loaded():
        log("Sollumz not loaded; cannot export.", log_file)
        return False

    utils_sollumz.select_geo()
    for obj in bpy.context.selected_objects:
        utils_sollumz.ensure_material(obj)

    export_op = utils_sollumz.find_op(["sollumz.export_assets"])
    if not export_op:
        log("Export operator missing.", log_file)
        return False

    try:
        export_op(directory=str(out_dir))
    except Exception as exc:
        log(f"Export error: {exc}", log_file)

    stream = out_dir / "fivem_resource" / resource_name / "stream"
    stream.mkdir(parents=True, exist_ok=True)
    # copy any generated files
    for ext in (".ydr", ".ydr.xml"):
        for obj in Path.cwd().glob(f"*{ext}"):
            (stream / obj.name).write_bytes(obj.read_bytes())

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
    args = parser.parse_args()
    run_export(args.mode, Path(args.output), args.resource_name, args.log)


if __name__ == "__main__":
    main()
