# DE Scripts MLO Studio

DE Scripts MLO Studio is a Windows desktop application that turns a prompt into a complete FiveM MLO resource folder. It assembles a build using existing MLO shells, adds prop placements as a YMAP, and exports a CodeWalker-friendly stub for final placement.

## Features

- Prompt → Plan → Placement pipeline with deterministic layouts.
- Asset-backed shell library with import-by-folder support.
- Generates CodeWalker-friendly PLACEME YMAP files.
- Preview schematic renderer with white background.
- Windows-ready PySide6 UI with DE Scripts branding.

## Quick Start

1. Install Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python -m app.main
   ```

## Shell Library

- Template catalog is stored in `assets/shell_library.json`.
- Import shells via the Shell Library tab. The files are copied to:
  `user_data/shells/<shell_name>/`

## Output Structure

```
<output>/<resource_name>/
  fxmanifest.lua
  stream/
    <resource_name>_PLACEME.ymap
  data/
    build_spec.json
    placements.json
  preview/
    preview.png
  README_CODEWALKER.md
```

## Release Build

Run `make_release.bat` to build a Windows executable using PyInstaller. Build artifacts are written to `/dist` and ignored by git.
