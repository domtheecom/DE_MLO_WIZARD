import os
from pathlib import Path


def export_resource(resource_name: str, ymap_xml: str) -> str:
    base_output = Path(__file__).resolve().parent / "output"
    resource_path = base_output / resource_name
    stream_path = resource_path / "stream"

    stream_path.mkdir(parents=True, exist_ok=True)

    ymap_path = stream_path / f"{resource_name}.ymap"
    ymap_path.write_text(ymap_xml, encoding="utf-8")

    fxmanifest = (
        "fx_version 'cerulean'\n"
        "game 'gta5'\n\n"
        f"this_is_a_map 'yes'\n\n"
        "files {\n"
        f"    'stream/{resource_name}.ymap'\n"
        "}\n"
    )
    (resource_path / "fxmanifest.lua").write_text(fxmanifest, encoding="utf-8")

    return str(resource_path)
