param(
    [Parameter(Mandatory = $true)][string]$Prompt,
    [Parameter(Mandatory = $true)][string]$Out,
    [string]$Place = "",
    [int]$Floors = 1,
    [switch]$SkipBlender,
    [switch]$SkipPackage
)

$ErrorActionPreference = "Stop"

$venvPath = Join-Path -Path $PSScriptRoot -ChildPath ".venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating Python 3.11+ virtual environment at $venvPath"
    python -m venv $venvPath
}

$pythonExe = Join-Path $venvPath "Scripts/python.exe"
if (!(Test-Path $pythonExe)) {
    $pythonExe = Join-Path $venvPath "bin/python"
}

Write-Host "Using Python: $pythonExe"
& $pythonExe -m pip install --upgrade pip > $null

$srcRoot = Join-Path $PSScriptRoot "src"
$floormapOut = Join-Path $Out "floorplan.json"
$planDoc = Join-Path $Out "PLAN.md"

New-Item -ItemType Directory -Force -Path $Out | Out-Null

Write-Host "Parsing prompt into floorplan..."
& $pythonExe "$srcRoot/prompt_to_floorplan.py" --prompt "$Prompt" --out $floormapOut --place "$Place" --floors $Floors --plan-doc $planDoc

if (!$SkipBlender) {
    $blenderPath = "blender"
    $blendFile = Join-Path $Out "blockout.blend"
    Write-Host "Running Blender headless build..."
    & $blenderPath -b -P "$srcRoot/blender/build_from_floorplan.py" -- --floorplan $floormapOut --output $Out --blend $blendFile

    Write-Host "Exporting via Sollumz operators if available..."
    & $blenderPath -b $blendFile -P "$srcRoot/blender/export_sollumz.py" -- --output $Out
}

if (!$SkipPackage) {
    Write-Host "Packaging FiveM resource..."
    & $pythonExe "$srcRoot/fivem/package_resource.py" --source $Out --resource-name "mlo_build" --place "$Place"
}

Write-Host "Done. Review PLAN.md and README in output for guidance."
