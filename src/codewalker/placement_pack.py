import argparse
from pathlib import Path

def build_docs(out_dir: Path, resource: str, coords):
    out_dir.mkdir(parents=True, exist_ok=True)
    placement_md = out_dir / "PLACEMENT.md"
    placement_md.write_text(
        "\n".join(
            [
                "# CodeWalker Placement",
                "1. Open CodeWalker, File > New YMAP.",
                "2. Import the template ymap XML provided.",
                "3. Adjust position/rotation to match coords below.",
                "4. Save YMAP into stream folder.",
                "",
                f"Suggested coords: {coords if coords else 'fill in manually'}",
            ]
        ),
        encoding="utf-8",
    )
    ymap_template = out_dir / f"{resource}_placement_template.ymap.xml"
    ymap_template.write_text("<!-- placeholder ymap -->", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--resource", required=True)
    ap.add_argument("--coords", default="")
    args = ap.parse_args()
    build_docs(Path(args.out), args.resource, args.coords)


if __name__ == "__main__":
    main()
