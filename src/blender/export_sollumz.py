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


if __name__ == "__main__":
    main()
