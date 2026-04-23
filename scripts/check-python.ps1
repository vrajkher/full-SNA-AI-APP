# Verifies a compatible Python is available and dependencies are installed.
# Run from an elevated PowerShell prompt on the target Windows machine.

$ErrorActionPreference = "Stop"

Write-Host "Accotech AI - environment check" -ForegroundColor Cyan

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    $python = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $python) {
    Write-Error "Python is not on PATH. Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
}

$version = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "Python: $python ($version)"

if ([version]$version -lt [version]"3.10") {
    Write-Error "Python >= 3.10 is required. Found $version."
    exit 1
}

$req = Join-Path $PSScriptRoot "..\backend\requirements.txt"
Write-Host "Installing backend dependencies from $req"
& $python -m pip install --upgrade pip | Out-Null
& $python -m pip install -r $req

Write-Host "Environment ready." -ForegroundColor Green
