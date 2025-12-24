# DE Scripts MLO Studio (Blender)

DE Scripts MLO Studio is a Blender 4.x add-on that generates a modular MLO building shell and interior layout from a text prompt, creates room/portal helpers, and exports a ready-to-drop FiveM resource using Sollumz.

## What it does
- Prompt → procedural shell + interior layout
- Optional furnishings placeholders for layout visualization
- Optional collision proxy
- Room and portal helper objects (best effort)
- One-click FiveM resource export (YDR/YBN/YTYP)

## Limitations
- This add-on generates geometry and simple placeholders only. It does **not** place GTA V props or assets.
- True GTA props require prop names and separate YDR assets. Use Sollumz and asset libraries to replace placeholders.

## Requirements
- Blender 4.x
- Sollumz add-on (required for export)

## Repo layout
```
DE_Scripts_MLO_Studio_Blender/
  addon/
  docs/
```

## Documentation
- [Install](docs/INSTALL.md)
- [Quickstart](docs/QUICKSTART.md)
- [Prompt format](docs/PROMPT_FORMAT.md)
