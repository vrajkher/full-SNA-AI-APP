#!/usr/bin/env bash
# ACCOTECH AI – One-line installer for macOS / Linux
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/vrajkher/full-sna-ai-app/claude/tally-automation-app-4nVx2/install.sh | bash
#
# Or locally:
#   bash install.sh
#
# What this does (one run, no further prompts):
#   1. Verifies python3 (>= 3.10), node, npm, git are available
#      (auto-installs via apt / brew when possible)
#   2. Clones / updates the repo into ~/.accotech/full-SNA-AI-APP
#   3. Creates a Python venv and installs backend dependencies
#   4. Installs frontend + electron dependencies
#   5. Builds the React frontend
#   6. Writes a ~/.local/bin/accotech launcher
#   7. Launches the app

set -euo pipefail

REPO_URL="${ACCOTECH_REPO_URL:-https://github.com/vrajkher/full-sna-ai-app.git}"
BRANCH="${ACCOTECH_BRANCH:-claude/tally-automation-app-4nVx2}"
INSTALL_DIR="${ACCOTECH_HOME:-$HOME/.accotech}"
REPO_DIR="$INSTALL_DIR/full-SNA-AI-APP"

c_blue=$'\033[36m'; c_green=$'\033[32m'; c_yellow=$'\033[33m'; c_red=$'\033[31m'; c_off=$'\033[0m'
log()   { printf "%s[%s]%s %s\n" "$c_blue"   "$(date +%H:%M:%S)" "$c_off" "$1"; }
ok()    { printf "%s[%s]%s %s\n" "$c_green"  "$(date +%H:%M:%S)" "$c_off" "$1"; }
warn()  { printf "%s[%s]%s %s\n" "$c_yellow" "$(date +%H:%M:%S)" "$c_off" "$1"; }
die()   { printf "%s[%s]%s %s\n" "$c_red"    "$(date +%H:%M:%S)" "$c_off" "$1" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

detect_installer() {
  if have brew;    then echo "brew"
  elif have apt-get; then echo "apt"
  elif have dnf;   then echo "dnf"
  elif have pacman; then echo "pacman"
  else echo "none"
  fi
}

PM=$(detect_installer)

pm_install() {
  local pkgs=("$@")
  case "$PM" in
    brew)   brew install "${pkgs[@]}" ;;
    apt)    sudo apt-get update -y && sudo apt-get install -y "${pkgs[@]}" ;;
    dnf)    sudo dnf install -y "${pkgs[@]}" ;;
    pacman) sudo pacman -Sy --noconfirm "${pkgs[@]}" ;;
    none)   die "No supported package manager (brew/apt/dnf/pacman) — install ${pkgs[*]} manually and re-run." ;;
  esac
}

ensure_python() {
  if have python3; then
    local ver
    ver=$(python3 -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    local major minor
    major=${ver%%.*}; minor=${ver##*.}
    if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; }; then
      ok "python3 $ver detected"; return
    fi
    warn "python3 $ver is too old (need >= 3.10)"
  fi
  log "Installing python3 + venv + pip..."
  case "$PM" in
    brew) pm_install python@3.12 ;;
    apt)  pm_install python3 python3-venv python3-pip ;;
    dnf)  pm_install python3 python3-pip ;;
    pacman) pm_install python python-pip ;;
    none) die "Install Python 3.10+ manually and re-run." ;;
  esac
}

ensure_node() {
  if have node; then ok "node $(node --version) detected"; return; fi
  log "Installing Node.js LTS..."
  case "$PM" in
    brew) pm_install node ;;
    apt)  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && pm_install nodejs ;;
    dnf)  pm_install nodejs ;;
    pacman) pm_install nodejs npm ;;
    none) die "Install Node.js LTS manually and re-run." ;;
  esac
}

ensure_git() {
  if have git; then return; fi
  log "Installing git..."
  pm_install git
}

ensure_git
ensure_python
ensure_node

mkdir -p "$INSTALL_DIR"

if [ -d "$REPO_DIR/.git" ]; then
  log "Updating existing checkout at $REPO_DIR"
  git -C "$REPO_DIR" fetch origin "$BRANCH" --depth 1
  git -C "$REPO_DIR" reset --hard "origin/$BRANCH"
else
  log "Cloning repository to $REPO_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

log "Creating Python venv..."
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
log "Installing backend requirements..."
python -m pip install -r backend/requirements.txt

log "Installing frontend dependencies..."
( cd frontend && npm install --no-audit --no-fund --loglevel=error )
log "Building frontend..."
( cd frontend && npm run build )

log "Installing electron dependencies..."
( cd electron && npm install --no-audit --no-fund --loglevel=error )

mkdir -p "$HOME/.local/bin"
LAUNCHER="$HOME/.local/bin/accotech"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
set -e
cd "$REPO_DIR"
export ACCOTECH_PYTHON="$REPO_DIR/.venv/bin/python"
export ACCOTECH_SKIP_BACKEND=0
cd electron
exec npm start
EOF
chmod +x "$LAUNCHER"

ok "Install complete."
ok "Launch with: accotech    (or run $LAUNCHER)"
log "Launching Accotech AI..."
exec "$LAUNCHER"
