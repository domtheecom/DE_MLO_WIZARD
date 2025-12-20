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


if __name__ == "__main__":
    main()
