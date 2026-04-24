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

$ErrorActionPreference  = "Stop"
$InformationPreference  = "Continue"
# Prevent native-command stderr writes (e.g. "No suitable Python runtime
# found" from py.exe) from being treated as terminating errors by the
# global ErrorActionPreference. We still hard-stop on cmdlet failures
# and on our own explicit Fail() calls.
$PSNativeCommandUseErrorActionPreference = $false

function Info($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Cyan }
function Okay($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Yellow }
function Fail($msg)  { Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $msg" -ForegroundColor Red; exit 1 }

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# Run a native command while tolerating stderr writes. PowerShell's strict
# $ErrorActionPreference="Stop" turns *any* stderr output from a native
# executable into a terminating NativeCommandError — even the benign
# "No suitable Python runtime found" message from py.exe. This helper
# isolates the probe so those writes can't abort the script.
function Invoke-Quiet {
    param([string]$Exe, [string[]]$CmdArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $out = & $Exe @CmdArgs 2>&1
        return @{ ExitCode = $LASTEXITCODE; Output = ($out | Out-String).Trim() }
    } catch {
        return @{ ExitCode = 1; Output = $_.Exception.Message }
    } finally {
        $ErrorActionPreference = $prev
        $global:LASTEXITCODE = 0
    }
}

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Ensure-Winget {
    if (-not (Have "winget")) {
        Fail "winget is required (Windows 10 1809+/Windows 11). Install 'App Installer' from the Microsoft Store and re-run."
    }
}

function Find-Python312 {
    # 1) py launcher is the most reliable locator on Windows
    if (Have "py") {
        $probe = Invoke-Quiet -Exe "py" -CmdArgs @("-3.12", "-c", "import sys; print(sys.executable)")
        if ($probe.ExitCode -eq 0 -and $probe.Output -and (Test-Path $probe.Output)) {
            return $probe.Output
        }
    }
    # 2) common install paths from winget / python.org
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "${env:ProgramFiles(x86)}\Python312\python.exe"
    )
    foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
    return $null
}

function Winget-Install($id, $label) {
    Info "Installing $label via winget..."
    $probe = Invoke-Quiet -Exe "winget" -CmdArgs @(
        "install", "--id", $id, "-e",
        "--accept-package-agreements", "--accept-source-agreements",
        "--silent", "--disable-interactivity"
    )
    # winget returns non-zero when a package is already installed; that is OK.
    if ($probe.ExitCode -ne 0) { Warn "winget exit=$($probe.ExitCode): $($probe.Output)" }
    Refresh-Path
}

function Ensure-Python312 {
    # Backend wheels (pandas, numpy, lxml) have the widest coverage on 3.12.
    # We always create the venv from 3.12 regardless of what's on PATH, so
    # a user's pre-existing Python 3.13 won't trigger a source build.
    $py = Find-Python312
    if ($py) { Okay "Python 3.12 found at $py"; return $py }

    Winget-Install "Python.Python.3.12" "Python 3.12"

    $py = Find-Python312
    if (-not $py) {
        Fail "Python 3.12 install did not expose a python.exe. Close this window, open a fresh admin PowerShell, and re-run the installer."
    }
    Okay "Python 3.12 installed at $py"
    return $py
}

function Ensure-Node {
    if (Have "node") {
        $probe = Invoke-Quiet -Exe "node" -CmdArgs @("--version")
        Okay "Node $($probe.Output) detected"
        return
    }
    Winget-Install "OpenJS.NodeJS.LTS" "Node.js LTS"
    if (-not (Have "node")) {
        Fail "Node install did not expose 'node' on PATH. Open a fresh terminal and re-run."
    }
}

function Ensure-Git {
    if (Have "git") { return }
    Winget-Install "Git.Git" "Git"
}

Ensure-Winget
$PythonExe = Ensure-Python312
Ensure-Node
Ensure-Git

$InstallDir = Join-Path $env:LOCALAPPDATA "Accotech"
$RepoDir    = Join-Path $InstallDir "full-SNA-AI-APP"
$RepoUrl    = "https://github.com/vrajkher/full-sna-ai-app.git"
$Branch     = "claude/tally-automation-app-4nVx2"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

function Assert-ExitCode($label) {
    if ($LASTEXITCODE -ne 0) { Fail "$label failed (exit=$LASTEXITCODE)" }
}

if (Test-Path $RepoDir) {
    Info "Updating existing checkout at $RepoDir"
    Push-Location $RepoDir
    git fetch origin $Branch --depth 1
    Assert-ExitCode "git fetch"
    git reset --hard "origin/$Branch" | Out-Null
    Assert-ExitCode "git reset"
    Pop-Location
} else {
    Info "Cloning repository to $RepoDir"
    git clone --depth 1 --branch $Branch $RepoUrl $RepoDir
    Assert-ExitCode "git clone"
}

Push-Location $RepoDir
try {
    Info "Creating Python 3.12 venv from $PythonExe..."
    if (-not (Test-Path ".venv")) {
        & $PythonExe -m venv .venv
        Assert-ExitCode "python -m venv"
    }
    $Py = Join-Path $RepoDir ".venv\Scripts\python.exe"
    & $Py -m pip install --upgrade pip wheel setuptools | Out-Null
    Assert-ExitCode "pip upgrade"

    Info "Installing backend requirements (binary wheels only)..."
    # --only-binary=:all: forces pip to refuse any source build.
    # If a wheel is missing we want to fail fast with a clear message
    # rather than try to compile C extensions on an end-user machine.
    & $Py -m pip install --only-binary=:all: -r backend\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Warn "Binary-only install failed; retrying with default resolver (may compile from source)"
        & $Py -m pip install -r backend\requirements.txt
        Assert-ExitCode "pip install backend requirements"
    }

    Info "Installing frontend dependencies..."
    Push-Location frontend
    npm install --no-audit --no-fund --loglevel=error
    Assert-ExitCode "npm install (frontend)"
    Info "Building frontend..."
    npm run build
    Assert-ExitCode "npm run build (frontend)"
    Pop-Location

    Info "Installing electron dependencies..."
    Push-Location electron
    npm install --no-audit --no-fund --loglevel=error
    Assert-ExitCode "npm install (electron)"
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
