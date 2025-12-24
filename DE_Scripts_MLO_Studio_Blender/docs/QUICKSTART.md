# Quickstart

## Example prompt
```
Miami Dade Fire Rescue House 51, 2 floors, 4 bays, chief office, dispatch, dorms, kitchen, gym/workout, wash bay, apron
```

## Steps
1. Open Blender and the **DE Scripts MLO Studio** panel.
2. Paste your prompt.
3. Set **Resource Name** and **Output Folder**.
4. Click **Build + Export**.

## Output
The exporter creates:
```
<output>/<resource_name>/
  fxmanifest.lua
  stream/<resource_name>.ydr
  stream/<resource_name>.ybn (if collision enabled)
  stream/<resource_name>.ytyp (best effort)
  meta/build_spec.json
  preview/preview.png (if enabled)
  README.md
```

## FiveM usage
1. Copy the resource folder into your server's `resources/` directory.
2. Add the resource name to `server.cfg`.
3. Restart your server.
