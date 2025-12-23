from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .fs_export import export_resource
from .planner import PlanResult, choose_shell, plan_layout
from .preview_render import PreviewRenderer
from .prompt_parser import ParsedPrompt, parse_prompt
from .shell_library import ShellLibrary


class BuildError(Exception):
    pass


def build_resource(
    base_dir: Path,
    prompt: str,
    resource_name: str,
    output_dir: Path,
    base_coords: tuple[float, float, float, float],
    shell_selection: str | None,
    copy_shell_files: bool,
    logger,
) -> Path:
    logger.info("Parsing prompt...")
    parsed = parse_prompt(prompt)

    library = ShellLibrary(base_dir)
    shells = library.load_shells()
    if not shells:
        raise BuildError("Shell library is empty. Import a shell to continue.")

    logger.info("Selecting shell...")
    shell = choose_shell(parsed, shells, shell_selection)

    logger.info("Planning layout...")
    props_catalog = base_dir / "assets" / "props_catalog.json"
    plan = plan_layout(parsed, shell, props_catalog)

    logger.info("Exporting resource...")
    shell_folder = None
    if copy_shell_files:
        shell_folder = library.user_data_dir / shell.shell_name
        if not shell_folder.exists():
            logger.warning("Shell folder not found in user data. Skipping shell file copy.")
            shell_folder = None

    build_spec = {
        "prompt": parsed.raw_prompt,
        "parsed": asdict(parsed),
        "shell": asdict(shell),
        "base_coords": {
            "x": base_coords[0],
            "y": base_coords[1],
            "z": base_coords[2],
            "heading": base_coords[3],
        },
        "modules": plan.modules,
    }

    codewalker_readme = _codewalker_instructions(resource_name)

    resource_dir = export_resource(
        output_dir=output_dir,
        resource_name=resource_name,
        plan=plan,
        placements=plan.placements,
        anchor_archetype="prop_roadcone02b",
        copy_shell=copy_shell_files,
        shell_folder=shell_folder,
        codewalker_readme=codewalker_readme,
        build_spec=build_spec,
    )

    preview = PreviewRenderer()
    preview.render(shell, plan.placements, resource_dir / "preview" / "preview.png")

    logger.info("Build complete: %s", resource_dir)
    return resource_dir


def _codewalker_instructions(resource_name: str) -> str:
    return (
        "# CodeWalker Placement Steps\n\n"
        "1. Open CodeWalker and load your GTA V project.\n"
        "2. Drag the generated resource into your FiveM server resources folder.\n"
        f"3. Open stream/{resource_name}_PLACEME.ymap in CodeWalker.\n"
        "4. Select the anchor prop at the origin (0,0,0) and move/rotate the map as needed.\n"
        "5. Export the final YMAP from CodeWalker once placement is correct.\n"
        "6. Replace the exported YMAP in the stream folder or create a new resource.\n"
    )
