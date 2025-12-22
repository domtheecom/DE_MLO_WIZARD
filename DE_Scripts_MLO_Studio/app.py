import json
import os
from datetime import datetime

from prompt_parser import parse_prompt
from layout_engine import build_layout, ModuleLibraryError
from portal_engine import build_portals
from furnishing_engine import build_furnishings, PropsLibraryError
from ymap_builder import build_ymap
from exporter import export_resource
from preview_renderer import render_preview


def run(prompt: str) -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_root = os.path.join(base_dir, "output")
    os.makedirs(output_root, exist_ok=True)

    spec = parse_prompt(prompt)
    module_library_path = os.path.join(base_dir, "module_library.json")
    props_library_path = os.path.join(base_dir, "assets", "props.json")

    try:
        layout = build_layout(spec, module_library_path)
    except ModuleLibraryError as exc:
        raise RuntimeError(str(exc)) from exc

    portals = build_portals(layout)

    try:
        furnishings = build_furnishings(layout, props_library_path)
    except PropsLibraryError as exc:
        raise RuntimeError(str(exc)) from exc

    ymap_xml = build_ymap(layout, furnishings)
    resource_path, ymap_path = export_resource(output_root, spec["resource_name"], ymap_xml)

    preview_path = os.path.join(resource_path, "preview.png")
    render_preview(layout, furnishings, preview_path)

    meta_path = os.path.join(resource_path, "meta.json")
    meta = {
        "prompt": prompt,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "spec": spec,
        "layout": layout,
        "portals": portals,
        "furnishings": furnishings,
    }
    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(meta, file, indent=2)

    return {
        "output_path": os.path.abspath(resource_path),
        "resource_name": spec["resource_name"],
        "ymap_path": os.path.abspath(ymap_path),
        "preview_png_path": os.path.abspath(preview_path),
        "meta_path": os.path.abspath(meta_path),
        "warnings": layout.get("warnings", []),
    }


__all__ = ["run"]
