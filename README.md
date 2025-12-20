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

## Examples
- `examples/station51_firehouse.txt`
- `examples/nightclub.txt`
- `examples/sandy_shores_motel.txt`
