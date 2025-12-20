<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
# DE_MLO_WIZARD

Beginner-focused, offline pipeline to generate FiveM MLO blockouts from a natural-language prompt. It runs from Windows PowerShell, drives Blender 4.5 LTS headless where possible, and uses the Sollumz add-on when available. If headless binary export is not possible, the tool guides you into a UI-based Final Export with exact next steps.

> No cloud APIs. Deterministic templates and a transparent floorplan you can edit.

## Quick Start (3 commands)
1) **Doctor**: verify Blender path, Sollumz visibility, Python, and write permissions.
```powershell
.\mlo.ps1 -Doctor -Out .\builds\station51
```

2) **Build**: generate floorplan, blockout blend, and attempt headless exports.
```powershell
.\mlo.ps1 -Prompt "Two-bay fire station with dorms" -Out .\builds\station51 -Place "Sandy Shores" -Floors 2
```

3) **Final Export (if needed)**: open Blender UI and export binaries.
```powershell
.\mlo.ps1 -FinalExport -Out .\builds\station51
```

## What You Get
- `floorplan.json` — deterministic, editable layout (rooms, corridors, stairs, doors, windows, bay openings)
- `PLAN.md` — human-readable plan for beginners
- `props_manifest.json` — placeholder prop hints you can replace later
- `blockout.blend` — Blender scene with geometry and helpers
- `fivem_resource/<name>/stream` — exports (.ydr/.ybn/.ytyp or XML placeholders)
- `fivem_resource/<name>/data` — docs and placement helpers

## How It Works
1) **Prompt → Floorplan** (`src/prompt_to_floorplan.py`)
   - Parses prompt into a structured plan using templates (fire station defaults included).
   - Outputs `floorplan.json`, `PLAN.md`, optional `mlo_meta.json`, and `props_manifest.json`.

2) **Blender Blockout** (`src/blender/build_from_floorplan.py`)
   - Runs headless: `blender -b -P build_from_floorplan.py -- --floorplan ... --output ... --blend ...`
   - Creates GEO/COLLISION/HELPERS/MLO collections and grid-aligned geometry.
   - Applies transforms and stacks floors using `floor_height`.

3) **Sollumz Export** (`src/blender/export_sollumz.py`)
   - Detects Sollumz dynamically (no hardcoded operator IDs).
   - Assigns materials if missing; exports into `fivem_resource/<name>/stream`.
   - If only XML appears, prints the exact Final Export command.

4) **Final Export UI Helper** (`src/blender/final_export_ui.py`)
   - Runs in Blender UI to attempt binary exports with a real context.
   - Writes `export_log.txt` for troubleshooting.

5) **FiveM Packager** (`src/fivem/package_resource.py`)
   - Generates `fxmanifest.lua`, README, placement helper, and copies docs into the resource.

## PowerShell Flags
- `-Prompt` **(required for build)**: natural-language description
- `-Out` **(required)**: output folder
- `-Place`: placement hint for CodeWalker docs
- `-Floors`: number of floors (default 1)
- `-FinalExport`: run Blender UI export helper on the existing blend
- `-Doctor`: environment checks
- `-SkipBlender`: reuse existing blend
- `-SkipPackage`: skip resource packaging
- `-BlenderPath`: override Blender auto-detection
- `-FullMLO` / `-NoProps` / `-NoPortals`: optional debug controls
- `-ResourceName`: resource folder name (default is output folder name)
- `-CoordsX -CoordsY -CoordsZ -Heading`: optional placement values for CodeWalker pack

## CodeWalker Placement Helper
The tool never assumes headless CodeWalker automation. It writes a guided checklist in:
`fivem_resource/<name>/data/PLACEMENT.md` with an XML template in the same folder.

## Troubleshooting
- **Blender not found**: add `blender.exe` to PATH or pass `-BlenderPath`.
- **Sollumz missing**: install and enable the add-on in Blender. Run `-Doctor` to verify.
- **Only XML exports**: run `-FinalExport` to attempt binary export in UI context.
- **Plan is wrong**: edit `PLAN.md`/`floorplan.json`, then re-run with `-SkipBlender`.

## Notes
- Blender supports headless scripting for automation.
- Sollumz supports GTA V asset creation including YDR/YBN/YTYP and partial YMAP via XML.
- Sollumz import workflow relies on CodeWalker XML exports for round-tripping.
=======
# mlo-ai-builder

Beginner-friendly PowerShell workflow that turns a natural-language description into a FiveM-ready MLO blockout using Blender running headless with Python scripting. It leans on the open-source Sollumz Blender add-on (supports GTA V formats including YDR/YBN/YTYP and partial YMAP via XML) and respects CodeWalker-driven XML imports.

> The pipeline uses deterministic templates instead of cloud LLMs. You always get a generated floorplan you can inspect and edit.

## Quickstart (Windows, PowerShell)
1. Install Blender (prefer an LTS build) and install the Sollumz add-on from the official releases page.
2. Clone/download this repo and open PowerShell in its root.
3. Run:
   ```powershell
   .\mlo.ps1 -Prompt "Two-bay firehouse with dorms and watch office" -Out .\builds\station51 -Place "Sandy Shores" -Floors 2
   ```
4. Blender runs headless (`blender.exe -b`) to build `blockout.blend`, then attempts Sollumz exports. If exports are not discoverable, follow the printed manual UI steps.
5. FiveM packaging drops files under `builds/<name>/fivem_resource/` with `fxmanifest.lua`, `PLACEMENT.md`, and copied JSON plan.

## CLI Overview
- `-Prompt` (required): natural-language description.
- `-Out` (required): output folder (blend, JSON, resource).
- `-Place`: placement hint for CodeWalker helper docs.
- `-Floors`: number of floors (default 1).
- `-SkipBlender`: reuse an existing blend without rebuilding.
- `-SkipPackage`: skip FiveM packaging.

## Pipeline
1. **Prompt parser** (`src/prompt_to_floorplan.py`): converts the prompt to `floorplan.json` and `PLAN.md` using building-type templates (fire station, police station, hospital, nightclub, warehouse, generic office). Defaults include 0.2 m wall thickness, ~3.2 m floor heights, and hallway widths tuned per template.
2. **Blender blockout** (`src/blender/build_from_floorplan.py`): executed via `blender -b -P ...` to build grid-aligned rectangular rooms, walls, ceilings, corridors, stairs, and an origin helper object. Collections: GEO, COLLISION, HELPERS. Objects prefixed `ROOM_`, `WALL_`, `CEIL_`, `STAIR_`, `DOORCUT_`, `BAYOPEN_` where applicable.
3. **Sollumz export** (`src/blender/export_sollumz.py`): introspects `bpy.ops` for operators containing `sollumz/export/ydr/ybn/ytyp/xml`. If found, it calls them and prints which operators ran. If not found or failing, it stops with manual export clicks you can follow in Blender.
4. **FiveM packager** (`src/fivem/package_resource.py`): creates `fxmanifest.lua`, README, placement helper, and copies `floorplan.json` for reference.

## Placement Helper (CodeWalker)
Headless CodeWalker automation is **not assumed**. The generated `PLACEMENT.md` provides a guided checklist:
1. Open CodeWalker, load the map.
2. Import XML generated by CodeWalker (Sollumz expects CodeWalker XMLs for round-tripping).
3. Create/position a YMAP for the MLO using suggested coordinates/rotation.
4. Save the YMAP and export XML to keep future Blender imports consistent.

## Performance and MLO Basics
- Keep walls/floors simple for early blockouts; add LODs and collision meshes as you polish.
- Use SOLLUMZ collision exports for COL meshes and keep portals/rooms organized if you extend into full MLO authoring.
- Maintain sensible hallway widths (2.2–3.0 m), door widths (1.0 m single, 1.8 m double, 3.5–4.5 m bay), and floor heights (~3.2 m by default).
- Place helper origin at 0,0,0 to align with FiveM placement.

## Troubleshooting
- **No Sollumz operators found**: ensure the add-on is installed and enabled in Blender. Re-run `.\mlo.ps1` or open the `.blend` and export manually following the printed steps.
- **Blender missing**: add `blender.exe` to PATH or edit `mlo.ps1` to point to your install.
- **Prompt looks wrong**: edit the generated `PLAN.md` or `floorplan.json` and re-run with `-SkipBlender` to skip regeneration.
>>>>>>> main

## Examples
- `examples/station51_firehouse.txt`
- `examples/nightclub.txt`
- `examples/sandy_shores_motel.txt`
<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
=======

## Notes on Capabilities
- Blender supports headless execution with Python scripting for automation.
- Sollumz is a Blender add-on for GTA V assets supporting YDR/YBN/YTYP and partial YMAP via XML, and its import workflow relies on XML exported from CodeWalker.
- Full CodeWalker placement automation is not guaranteed; default to the provided checklist unless you provide a working API.
>>>>>>> main
