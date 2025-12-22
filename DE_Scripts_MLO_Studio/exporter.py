import os
from typing import Tuple


def export_resource(output_root: str, resource_name: str, ymap_xml: str) -> Tuple[str, str]:
    resource_path = os.path.join(output_root, resource_name)
    stream_path = os.path.join(resource_path, "stream")
    os.makedirs(stream_path, exist_ok=True)

    ymap_filename = f"{resource_name}.ymap"
    ymap_path = os.path.join(stream_path, ymap_filename)
    with open(ymap_path, "w", encoding="utf-8") as file:
        file.write(ymap_xml)

    fxmanifest_path = os.path.join(resource_path, "fxmanifest.lua")
    with open(fxmanifest_path, "w", encoding="utf-8") as file:
        file.write(
            "fx_version 'cerulean'\n"
            "game 'gta5'\n\n"
            "this_is_a_map 'yes'\n"
            "files {\n"
            f"  'stream/{ymap_filename}',\n"
            "}\n"
        )

    return resource_path, ymap_path


__all__ = ["export_resource"]
