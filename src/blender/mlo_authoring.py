import argparse
import json
from pathlib import Path
import bpy
from . import utils_sollumz


def log(msg, path):
    print(msg)
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--floorplan", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log")
    parser.add_argument("--no-portals", action="store_true")
    args = parser.parse_args()

    with open(args.floorplan, "r", encoding="utf-8") as f:
        plan = json.load(f)

    if not utils_sollumz.is_sollumz_loaded():
        log("Sollumz not detected; writing debug meta only.", args.log)
        debug = Path(args.output) / "mlo_meta_debug.md"
        debug.write_text("Sollumz not available; portals/rooms not authored.", encoding="utf-8")
        return

    log("Creating basic MLO containers (placeholder).", args.log)
    # Minimal placeholder; real ops may differ and are handled by UI export stage.
    return


if __name__ == "__main__":
    main()
