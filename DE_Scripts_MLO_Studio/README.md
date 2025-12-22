# DE Scripts MLO Studio

A branded, offline desktop app for generating FiveM-ready MLO resources with YMAP XML and a clean preview image.

## Features
- Dark, modern UI with cyan → magenta accents and DE Scripts branding
- Builds a drop-in FiveM resource with `fxmanifest.lua` + `stream/*.ymap`
- Generates a **white-background** preview image (`preview.png`) of the layout
- Deterministic module placement (no Blender or CodeWalker automation)
- Packaged EXE via PyInstaller

## Requirements
- **Python 3.11+**
- Tkinter (ships with standard Python on Windows)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Run the App
```bash
python ui.py
```

## Output
Every build writes a full resource to:
```
DE_Scripts_MLO_Studio/output/de_scripts_mlo_<type>/
```
Contents:
- `fxmanifest.lua`
- `stream/de_scripts_mlo_<type>.ymap`
- `preview.png`
- `meta.json`

## Drop into FiveM
1. Copy the generated folder into your server resources directory.
2. Add to your `server.cfg`:
```
ensure de_scripts_mlo_<type>
```

## Replace the Logo
Replace the placeholder image at:
```
assets/de_scripts_logo.png
```
The UI will show your logo automatically. If the file is missing, the app displays the title text only.

## Set Real Archetypes
`module_library.json` contains placeholder archetypes. Replace them with valid archetype names from your DLC/custom packs.
If a name starts with `v_` or includes `placeholder`, the app will warn you that it might not exist.

## Build a Windows EXE
Run from the project root:
```bat
make_release.bat
```
This creates:
```
release/DEScriptsMLOStudio/
```
Distribute the folder or zip it. Users can run the EXE without installing Python.

## Notes
- **No mesh generation**. The app only places existing archetypes and props.
- **No Blender** and **no CodeWalker automation** required.
