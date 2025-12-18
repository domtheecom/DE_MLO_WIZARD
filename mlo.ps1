[CmdletBinding(DefaultParameterSetName = "Build")]
param(
    [Parameter(ParameterSetName = "Build", Mandatory = $true)][string]$Prompt,
    [Parameter(Mandatory = $true)][string]$Out,
    [string]$Place = "",
    [int]$Floors = 1,
    [switch]$SkipBlender,
    [switch]$SkipPackage,
    [switch]$FinalExport,
    [switch]$Doctor,
    [switch]$FullMLO = $true,
    [switch]$NoProps,
    [switch]$NoPortals,
    [string]$BlenderPath,
    [string]$ResourceName,
    [double]$CoordsX,
    [double]$CoordsY,
    [double]$CoordsZ,
    [double]$Heading
)

$ErrorActionPreference = "Stop"

function Write-RunLog {
    param([string]$Path, [string]$Message)
    $timestamp = (Get-Date).ToString("s")
    Add-Content -Path $Path -Value "[$timestamp] $Message"
}

function Resolve-BlenderPath {
    param([string]$Override)
    if ($Override) { return $Override }
    $cmd = Get-Command blender -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $defaultPath = "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe"
    if (Test-Path $defaultPath) { return $defaultPath }
    throw "Blender not found. Add blender.exe to PATH or provide -BlenderPath. Expected at $defaultPath"
}

try {
    $resolvedOut = Resolve-Path -Path $Out -ErrorAction SilentlyContinue
    if ($resolvedOut) { $Out = $resolvedOut.Path } else { $Out = [System.IO.Path]::GetFullPath($Out) }
} catch { $Out = [System.IO.Path]::GetFullPath($Out) }

New-Item -ItemType Directory -Force -Path $Out | Out-Null
$runLog = Join-Path $Out "run_log.txt"
$exportLog = Join-Path $Out "export_log.txt"
Write-RunLog -Path $runLog -Message "Starting mlo.ps1 with FinalExport=$FinalExport Doctor=$Doctor"

$blendFile = Join-Path $Out "blockout.blend"
$floormapOut = Join-Path $Out "floorplan.json"
$planDoc = Join-Path $Out "PLAN.md"
$mloMeta = Join-Path $Out "mlo_meta.json"
$propsManifest = Join-Path $Out "props_manifest.json"
$resourceNameUsed = if ($ResourceName) { $ResourceName } else { Split-Path -Path $Out -Leaf }

# venv bootstrap
$venvPath = Join-Path -Path $PSScriptRoot -ChildPath ".venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating Python 3.11+ virtual environment at $venvPath"
    python -m venv $venvPath
}
$pythonExe = Join-Path $venvPath "Scripts/python.exe"
if (!(Test-Path $pythonExe)) { $pythonExe = Join-Path $venvPath "bin/python" }
Write-Host "Using Python: $pythonExe"
& $pythonExe -m pip install --upgrade pip > $null

$srcRoot = Join-Path $PSScriptRoot "src"
$blenderPathResolved = Resolve-BlenderPath -Override $BlenderPath
Write-RunLog -Path $runLog -Message "Blender resolved to $blenderPathResolved"

function Run-Doctor {
    Write-Host "Doctor checks..."
    Write-RunLog -Path $runLog -Message "Doctor started"
    Write-Host "Blender path: $blenderPathResolved"
    try {
        $blenderVersion = & $blenderPathResolved --version
        Write-Host $blenderVersion
        Write-RunLog -Path $runLog -Message "Blender version check ok"
    } catch { Write-RunLog -Path $runLog -Message "Blender version check failed: $_" }

    $tmpScript = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "sollumz_check.py")
    @"
import addon_utils
found = False
for mod in addon_utils.modules():
    if mod.__name__.lower() == "sollumz":
        found = True
print(f"SOLLUMZ_FOUND={found}")
"@ | Set-Content -Path $tmpScript -Encoding UTF8
    try {
        $detectOutput = & $blenderPathResolved -b -P $tmpScript --
        Write-Host $detectOutput
        Write-RunLog -Path $runLog -Message "Sollumz detection output: $detectOutput"
    } catch { Write-RunLog -Path $runLog -Message "Sollumz detection failed: $_" }

    try {
        $pyVer = & $pythonExe --version
        Write-Host "Python: $pyVer"
        Write-RunLog -Path $runLog -Message "Python version: $pyVer"
    } catch { Write-RunLog -Path $runLog -Message "Python check failed: $_" }

    $streamDir = Join-Path $Out "fivem_resource/$resourceNameUsed/stream"
    $writable = $false
    try {
        New-Item -ItemType Directory -Force -Path $streamDir | Out-Null
        $probe = Join-Path $streamDir "__write_test.txt"
        "probe" | Set-Content -Path $probe
        Remove-Item $probe -Force
        $writable = $true
    } catch {}
    Write-Host "Stream dir: $streamDir (writable=$writable)"
    Write-RunLog -Path $runLog -Message "Stream dir writable=$writable"

    Write-Host "Doctor complete."
    Write-RunLog -Path $runLog -Message "Doctor complete"
}

if ($Doctor) {
    Run-Doctor
    if (-not $FinalExport -and -not $Prompt) { return }
}

if ($FinalExport) {
    Write-Host "Launching Blender UI for Final Export..."
    Write-RunLog -Path $runLog -Message "FinalExport starting with blend $blendFile"
    & $blenderPathResolved $blendFile -P "$srcRoot/blender/final_export_ui.py" -- --output $Out --log $exportLog --resource-name $resourceNameUsed
    Write-Host "Final export attempted. Check stream folder and export_log.txt."
    return
}

if (-not $Prompt) {
    throw "-Prompt is required for build runs. Use -FinalExport to finalize an existing blend or -Doctor for checks."
}

Write-Host "Parsing prompt into floorplan..."
Write-RunLog -Path $runLog -Message "Parsing prompt"
$fullMloFlag = if ($FullMLO) { "--full-mlo" } else { "" }
$propsFlag = if ($NoProps) { "--no-props" } else { "" }
$portalsFlag = if ($NoPortals) { "--no-portals" } else { "" }
& $pythonExe "$srcRoot/prompt_to_floorplan.py" --prompt "$Prompt" --out $floormapOut --place "$Place" --floors $Floors --plan-doc $planDoc --mlo-meta $mloMeta $fullMloFlag $propsFlag $portalsFlag

if (-not $SkipBlender) {
    Write-Host "Running Blender headless build..."
    Write-RunLog -Path $runLog -Message "Starting Blender build"
    & $blenderPathResolved -b -P "$srcRoot/blender/build_from_floorplan.py" -- --floorplan $floormapOut --output $Out --blend $blendFile --full-mlo $FullMLO --no-props:$NoProps --no-portals:$NoPortals

    if ($FullMLO) {
        Write-Host "Authoring MLO structures..."
        Write-RunLog -Path $runLog -Message "MLO authoring"
        & $blenderPathResolved -b $blendFile -P "$srcRoot/blender/mlo_authoring.py" -- --floorplan $floormapOut --output $Out --log $runLog --no-portals:$NoPortals
    }

    Write-Host "Exporting via Sollumz (headless XML-first)..."
    Write-RunLog -Path $runLog -Message "Starting headless export"
    & $blenderPathResolved -b $blendFile -P "$srcRoot/blender/export_sollumz.py" -- --output $Out --mode headless_xml --resource-name $resourceNameUsed --log $exportLog
}

if (-not $SkipPackage) {
    Write-Host "Packaging FiveM resource ($resourceNameUsed)..."
    Write-RunLog -Path $runLog -Message "Packaging resource $resourceNameUsed"
    & $pythonExe "$srcRoot/fivem/package_resource.py" --source $Out --resource-name $resourceNameUsed --place "$Place" --coordsx $CoordsX --coordsy $CoordsY --coordsz $CoordsZ --heading $Heading
}

$streamPath = Join-Path $Out "fivem_resource/$resourceNameUsed/stream"
if (!(Test-Path $streamPath)) { New-Item -ItemType Directory -Force -Path $streamPath | Out-Null }
$blendPathMsg = "Blockout blend: $blendFile"
$streamMsg = "Stream folder: $streamPath"
Write-Host $blendPathMsg
Write-Host $streamMsg
Write-RunLog -Path $runLog -Message $blendPathMsg
Write-RunLog -Path $runLog -Message $streamMsg

$ydrFiles = Get-ChildItem -Path $streamPath -Filter *.ydr -ErrorAction SilentlyContinue
if ($ydrFiles) {
    Write-Host "SUCCESS: Binary exports found." -ForegroundColor Green
    foreach ($f in $ydrFiles) { Write-Host " - $($f.FullName)" }
    Write-RunLog -Path $runLog -Message "Binary exports present"
} else {
    Write-Host "Headless export produced XML only or failed. Run Final Export if you need binaries:" -ForegroundColor Yellow
    Write-Host " .\\mlo.ps1 -FinalExport -Out $Out" -ForegroundColor Yellow
    Write-RunLog -Path $runLog -Message "Binary exports missing. Prompted user to run FinalExport."
}

Write-Host "Done. Review PLAN.md and README in output for guidance."
Write-RunLog -Path $runLog -Message "Run complete"
