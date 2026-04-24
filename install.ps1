# ACCOTECH AI – One-click installer for Windows
# Usage (from any PowerShell, run as Administrator):
#   iwr -useb https://raw.githubusercontent.com/vrajkher/full-sna-ai-app/claude/tally-automation-app-4nVx2/install.ps1 | iex
#
# Or locally:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#
# What this does (single run, no further prompts):
#   1. Installs Python 3.12 via winget (if missing)
#   2. Installs Node.js LTS via winget (if missing)
#   3. Clones / updates the Accotech AI repo into %LOCALAPPDATA%\Accotech
#   4. Creates a Python venv and installs backend dependencies
#   5. Installs frontend + electron npm dependencies
#   6. Builds the React frontend
#   7. Drops a desktop shortcut that launches the app
#   8. Launches the app

$ErrorActionPreference = "Stop"
$InformationPreference  = "Continue"

function Info($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Cyan }
function Okay($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Yellow }
function Fail($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Red; exit 1 }

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Ensure-Winget {
    if (-not (Have "winget")) {
        Fail "winget is required (Windows 10 1809+/Windows 11). Install 'App Installer' from the Microsoft Store and re-run."
    }
}

function Ensure-Python {
    if (Have "python") {
        $ver = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ([version]$ver -ge [version]"3.10") { Okay "Python $ver detected"; return }
    }
    Info "Installing Python 3.12 via winget..."
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements -h | Out-Null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
    if (-not (Have "python")) { Fail "Python install did not expose 'python' on PATH. Open a fresh terminal and re-run." }
}

function Ensure-Node {
    if (Have "node") { Okay "Node $((node --version)) detected"; return }
    Info "Installing Node.js LTS via winget..."
    winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements -h | Out-Null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
    if (-not (Have "node")) { Fail "Node install did not expose 'node' on PATH. Open a fresh terminal and re-run." }
}

function Ensure-Git {
    if (Have "git") { return }
    Info "Installing Git via winget..."
    winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements -h | Out-Null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

Ensure-Winget
Ensure-Python
Ensure-Node
Ensure-Git

$InstallDir = Join-Path $env:LOCALAPPDATA "Accotech"
$RepoDir    = Join-Path $InstallDir "full-SNA-AI-APP"
$RepoUrl    = "https://github.com/vrajkher/full-sna-ai-app.git"
$Branch     = "claude/tally-automation-app-4nVx2"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

if (Test-Path $RepoDir) {
    Info "Updating existing checkout at $RepoDir"
    Push-Location $RepoDir
    git fetch origin $Branch --depth 1 | Out-Null
    git reset --hard "origin/$Branch" | Out-Null
    Pop-Location
} else {
    Info "Cloning repository to $RepoDir"
    git clone --depth 1 --branch $Branch $RepoUrl $RepoDir
}

Push-Location $RepoDir
try {
    Info "Creating Python venv..."
    if (-not (Test-Path ".venv")) { python -m venv .venv }
    $Py = Join-Path $RepoDir ".venv\Scripts\python.exe"
    & $Py -m pip install --upgrade pip | Out-Null
    Info "Installing backend requirements..."
    & $Py -m pip install -r backend\requirements.txt

    Info "Installing frontend dependencies..."
    Push-Location frontend
    npm install --no-audit --no-fund --loglevel=error
    Info "Building frontend..."
    npm run build
    Pop-Location

    Info "Installing electron dependencies..."
    Push-Location electron
    npm install --no-audit --no-fund --loglevel=error
    Pop-Location

    # --- Launcher ---
    $Launcher = Join-Path $RepoDir "launch.cmd"
    @"
@echo off
setlocal
cd /d "%~dp0"
set ACCOTECH_PYTHON=%~dp0.venv\Scripts\python.exe
set ACCOTECH_SKIP_BACKEND=0
cd electron
call npm start
"@ | Set-Content -Encoding ASCII -Path $Launcher

    # --- Desktop shortcut ---
    $Shortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Accotech AI.lnk"
    $wsh = New-Object -ComObject WScript.Shell
    $lnk = $wsh.CreateShortcut($Shortcut)
    $lnk.TargetPath = $Launcher
    $lnk.WorkingDirectory = $RepoDir
    $lnk.IconLocation = "$RepoDir\electron\build\icon.ico,0"
    $lnk.WindowStyle = 7
    $lnk.Save()
    Okay "Desktop shortcut created: $Shortcut"

    # --- Start-menu shortcut ---
    $StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Accotech AI.lnk"
    $lnk2 = $wsh.CreateShortcut($StartMenu)
    $lnk2.TargetPath = $Launcher
    $lnk2.WorkingDirectory = $RepoDir
    $lnk2.WindowStyle = 7
    $lnk2.Save()
    Okay "Start-Menu shortcut created"

    Okay "Install complete. Launching Accotech AI..."
    Start-Process -FilePath $Launcher -WorkingDirectory $RepoDir
}
finally {
    Pop-Location
}
