#!/usr/bin/env bash
# =============================================================================
#  INCEPT.sh — Installation Script
#  https://github.com/0-Time/INCEPT.sh
#
#  Installs INCEPT.sh and all dependencies on Linux (Debian/Ubuntu, RHEL/Fedora,
#  Arch, openSUSE). Requires root or sudo access.
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/0-Time/INCEPT.sh/main/install.sh | bash
#    — or —
#    bash install.sh [--prefix /usr/local] [--no-model] [--uninstall]
# =============================================================================

set -euo pipefail

# ── Constants ────────────────────────────────────────────────────────────────

REPO_URL="https://github.com/0-Time/INCEPT.sh.git"
MODEL_FILENAME="incept-sh.gguf"
MODEL_URL="https://huggingface.co/0Time/INCEPT-SH/resolve/main/${MODEL_FILENAME}"
INSTALL_DIR="/opt/incept-sh"
BIN_LINK="/usr/local/bin/incept"
MODEL_DIR="${INSTALL_DIR}/models"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=11
LOG_FILE="/tmp/incept-sh-install.log"

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Flags ────────────────────────────────────────────────────────────────────

OPT_PREFIX="/usr/local"
OPT_NO_MODEL=false
OPT_UNINSTALL=false

for arg in "$@"; do
    case "$arg" in
        --prefix=*) OPT_PREFIX="${arg#*=}" ;;
        --no-model)  OPT_NO_MODEL=true ;;
        --uninstall) OPT_UNINSTALL=true ;;
        --help|-h)
            echo "Usage: bash install.sh [--prefix PATH] [--no-model] [--uninstall]"
            echo ""
            echo "  --prefix PATH   Installation prefix (default: /usr/local)"
            echo "  --no-model      Skip model download (place manually in ${MODEL_DIR})"
            echo "  --uninstall     Remove INCEPT.sh from this system"
            exit 0
            ;;
        *) echo "Unknown option: $arg" >&2; exit 1 ;;
    esac
done

BIN_LINK="${OPT_PREFIX}/bin/incept"

# ── Helpers ──────────────────────────────────────────────────────────────────

log()     { echo -e "${BOLD}[INCEPT.sh]${RESET} $*" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}${BOLD}  ✓${RESET}  $*" | tee -a "$LOG_FILE"; }
warn()    { echo -e "${YELLOW}${BOLD}  ⚠${RESET}  $*" | tee -a "$LOG_FILE"; }
error()   { echo -e "${RED}${BOLD}  ✗${RESET}  $*" | tee -a "$LOG_FILE" >&2; }
die()     { error "$*"; echo -e "\n${RED}Installation failed.${RESET} See log: ${LOG_FILE}" >&2; exit 1; }
step()    { echo -e "\n${CYAN}${BOLD}▸ $*${RESET}" | tee -a "$LOG_FILE"; }

require_root() {
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo &>/dev/null; then
            SUDO="sudo"
        else
            die "This script must be run as root, or sudo must be available."
        fi
    else
        SUDO=""
    fi
}

confirm() {
    local prompt="$1"
    local reply
    read -r -p "$(echo -e "${YELLOW}${BOLD}  ?${RESET}  ${prompt} [y/N] ")" reply
    [[ "${reply,,}" == "y" ]]
}

# ── Uninstall ────────────────────────────────────────────────────────────────

do_uninstall() {
    log "Uninstalling INCEPT.sh..."

    if [[ ! -d "$INSTALL_DIR" && ! -L "$BIN_LINK" ]]; then
        warn "INCEPT.sh does not appear to be installed."
        exit 0
    fi

    confirm "This will remove INCEPT.sh from ${INSTALL_DIR} and ${BIN_LINK}. Continue?" || {
        log "Uninstall cancelled."
        exit 0
    }

    require_root

    if [[ -L "$BIN_LINK" || -f "$BIN_LINK" ]]; then
        $SUDO rm -f "$BIN_LINK"
        success "Removed binary: ${BIN_LINK}"
    fi

    if [[ -d "$INSTALL_DIR" ]]; then
        $SUDO rm -rf "$INSTALL_DIR"
        success "Removed installation: ${INSTALL_DIR}"
    fi

    success "INCEPT.sh uninstalled."
    exit 0
}

[[ "$OPT_UNINSTALL" == true ]] && do_uninstall

# ── Banner ───────────────────────────────────────────────────────────────────

echo ""
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
  ██╗███╗   ██╗ ██████╗███████╗██████╗ ████████╗  ┃  ███████╗██╗  ██╗
  ██║████╗  ██║██╔════╝██╔════╝██╔══██╗╚══██╔══╝  ┃  ██╔════╝██║  ██║
  ██║██╔██╗ ██║██║     █████╗  ██████╔╝   ██║     ┃  ███████╗███████║
  ██║██║╚██╗██║██║     ██╔══╝  ██╔═══╝    ██║     ┃  ╚════██║██╔══██║
  ██║██║ ╚████║╚██████╗███████╗██║        ██║     ┃  ███████║██║  ██║
  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝        ╚═╝     ┃  ╚══════╝╚═╝  ╚═╝
BANNER
echo -e "${RESET}"
echo -e "  ${BOLD}Offline Command Inference Engine for Linux${RESET}"
echo -e "  https://github.com/0-Time/INCEPT.sh"
echo ""

# ── System Check ─────────────────────────────────────────────────────────────

step "Checking system requirements"

if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    DISTRO="${ID:-unknown}"
    DISTRO_LIKE="${ID_LIKE:-}"
    success "Detected: ${PRETTY_NAME:-$DISTRO}"
else
    warn "Cannot detect Linux distribution — proceeding with generic install."
    DISTRO="unknown"
    DISTRO_LIKE=""
fi

ARCH="$(uname -m)"
case "$ARCH" in
    x86_64|aarch64|arm64) success "Architecture: ${ARCH}" ;;
    *) die "Unsupported architecture: ${ARCH}. INCEPT.sh requires x86_64 or aarch64." ;;
esac

if command -v free &>/dev/null; then
    FREE_MB=$(free -m | awk '/^Mem:/{print $7}')
    if [[ "$FREE_MB" -lt 1500 ]]; then
        warn "Low available RAM: ${FREE_MB}MB. INCEPT.sh requires ~1GB free at runtime."
    else
        success "Available RAM: ${FREE_MB}MB"
    fi
fi

INSTALL_PARENT="$(dirname "$INSTALL_DIR")"
mkdir -p "$INSTALL_PARENT" 2>/dev/null || true
FREE_DISK_MB=$(df -m "$INSTALL_PARENT" 2>/dev/null | awk 'NR==2{print $4}' || echo 9999)
if [[ "$FREE_DISK_MB" -lt 2000 ]]; then
    die "Insufficient disk space: ${FREE_DISK_MB}MB available, ~2GB required."
else
    success "Available disk: ${FREE_DISK_MB}MB"
fi

require_root

# ── Package Manager Detection ─────────────────────────────────────────────────

step "Detecting package manager"

PKG_MANAGER=""
PKG_UPDATE=""
PKG_INSTALL=""

if command -v apt-get &>/dev/null; then
    PKG_MANAGER="apt"
    PKG_UPDATE="$SUDO apt-get update -qq"
    PKG_INSTALL="$SUDO apt-get install -y -qq"
    success "Package manager: apt (Debian/Ubuntu)"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
    PKG_UPDATE="$SUDO dnf check-update -q || true"
    PKG_INSTALL="$SUDO dnf install -y -q"
    success "Package manager: dnf (Fedora/RHEL)"
elif command -v yum &>/dev/null; then
    PKG_MANAGER="yum"
    PKG_UPDATE="$SUDO yum check-update -q || true"
    PKG_INSTALL="$SUDO yum install -y -q"
    success "Package manager: yum (CentOS/RHEL)"
elif command -v pacman &>/dev/null; then
    PKG_MANAGER="pacman"
    PKG_UPDATE="$SUDO pacman -Sy --noconfirm"
    PKG_INSTALL="$SUDO pacman -S --noconfirm --needed"
    success "Package manager: pacman (Arch)"
elif command -v zypper &>/dev/null; then
    PKG_MANAGER="zypper"
    PKG_UPDATE="$SUDO zypper refresh -q"
    PKG_INSTALL="$SUDO zypper install -y -q"
    success "Package manager: zypper (openSUSE)"
else
    die "No supported package manager found (apt, dnf, yum, pacman, zypper)."
fi

# ── System Dependencies ───────────────────────────────────────────────────────

step "Installing system dependencies"

log "Updating package index..."
eval "$PKG_UPDATE" >> "$LOG_FILE" 2>&1 || warn "Package index update failed — continuing."

# ── Python + venv (install BOTH together on apt) ──────────────────────────────

install_python() {
    log "Installing Python 3.11+..."
    case "$PKG_MANAGER" in
        apt)
            # Install python3 + venv + dev headers in one shot
            # Ubuntu 24.04 ships 3.12; Ubuntu 22.04 ships 3.10 (needs deadsnakes)
            local py_ver=""
            for v in python3.12 python3.11; do
                if $PKG_INSTALL ${v} ${v}-venv ${v}-dev >> "$LOG_FILE" 2>&1; then
                    py_ver="$v"
                    break
                fi
            done
            if [[ -z "$py_ver" ]]; then
                log "Trying deadsnakes PPA for Python 3.11..."
                $PKG_INSTALL software-properties-common >> "$LOG_FILE" 2>&1 || true
                $SUDO add-apt-repository -y ppa:deadsnakes/ppa >> "$LOG_FILE" 2>&1 \
                    || die "Failed to add deadsnakes PPA."
                $SUDO apt-get update -qq >> "$LOG_FILE" 2>&1
                $PKG_INSTALL python3.11 python3.11-venv python3.11-dev >> "$LOG_FILE" 2>&1 \
                    || die "Failed to install Python 3.11."
            fi
            ;;
        dnf|yum)
            $PKG_INSTALL python3.11 python3.11-devel >> "$LOG_FILE" 2>&1 \
                || die "Failed to install Python 3.11."
            ;;
        pacman)
            $PKG_INSTALL python >> "$LOG_FILE" 2>&1 \
                || die "Failed to install Python."
            ;;
        zypper)
            $PKG_INSTALL python311 python311-devel >> "$LOG_FILE" 2>&1 \
                || die "Failed to install Python 3.11."
            ;;
    esac
}

# Ensure venv package is installed for the detected Python on apt systems
ensure_venv_package() {
    local python_bin="$1"
    local py_ver
    py_ver=$("$python_bin" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

    if [[ "$PKG_MANAGER" == "apt" ]]; then
        log "Ensuring python${py_ver}-venv is installed..."
        $PKG_INSTALL "python${py_ver}-venv" >> "$LOG_FILE" 2>&1 || true
    fi
}

# Detect usable Python 3.11+
PYTHON=""
for candidate in python3.12 python3.11 python3 python; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major="${ver%%.*}"
        minor="${ver##*.}"
        if [[ "$major" -ge "$PYTHON_MIN_MAJOR" && "$minor" -ge "$PYTHON_MIN_MINOR" ]]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    warn "Python 3.11+ not found — attempting to install..."
    install_python
    for candidate in python3.12 python3.11 python3; do
        if command -v "$candidate" &>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    done
    [[ -n "$PYTHON" ]] || die "Python 3.11+ installation failed."
fi

# Always ensure the venv package matches the detected Python
ensure_venv_package "$PYTHON"

success "Python: $($PYTHON --version)"

# git
if ! command -v git &>/dev/null; then
    log "Installing git..."
    eval "$PKG_INSTALL git" >> "$LOG_FILE" 2>&1 || die "Failed to install git."
fi
success "git: $(git --version)"

# curl
if ! command -v curl &>/dev/null; then
    log "Installing curl..."
    eval "$PKG_INSTALL curl" >> "$LOG_FILE" 2>&1 || die "Failed to install curl."
fi
success "curl: $(curl --version | head -1)"

# pip
if ! $PYTHON -m pip --version &>/dev/null 2>&1; then
    log "Installing pip..."
    case "$PKG_MANAGER" in
        apt)     $PKG_INSTALL python3-pip >> "$LOG_FILE" 2>&1 || true ;;
        dnf|yum) $PKG_INSTALL python3-pip >> "$LOG_FILE" 2>&1 || true ;;
        pacman)  $PKG_INSTALL python-pip  >> "$LOG_FILE" 2>&1 || true ;;
        zypper)  $PKG_INSTALL python3-pip >> "$LOG_FILE" 2>&1 || true ;;
    esac
fi
$PYTHON -m pip --version &>/dev/null 2>&1 \
    && success "pip: $($PYTHON -m pip --version | awk '{print $1, $2}')" \
    || warn "pip not available — will use venv's pip instead."

# ── llama.cpp (llama-server) ──────────────────────────────────────────────────

step "Installing llama.cpp (llama-server)"

install_llamacpp() {
    log "Building llama-server from source..."

    case "$PKG_MANAGER" in
        apt)     $PKG_INSTALL build-essential cmake libgomp1 >> "$LOG_FILE" 2>&1 ;;
        dnf|yum) $PKG_INSTALL gcc gcc-c++ cmake libgomp    >> "$LOG_FILE" 2>&1 ;;
        pacman)  $PKG_INSTALL base-devel cmake              >> "$LOG_FILE" 2>&1 ;;
        zypper)  $PKG_INSTALL gcc gcc-c++ cmake libgomp1    >> "$LOG_FILE" 2>&1 ;;
    esac

    local build_dir
    build_dir="$(mktemp -d /tmp/llama-cpp-build.XXXXXX)"
    trap 'rm -rf "$build_dir"' RETURN

    log "Cloning llama.cpp..."
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$build_dir" >> "$LOG_FILE" 2>&1 \
        || die "Failed to clone llama.cpp."

    log "Building (this may take 5–15 minutes)..."
    cmake -S "$build_dir" -B "$build_dir/build" \
        -DLLAMA_BUILD_SERVER=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=OFF \
        >> "$LOG_FILE" 2>&1 || die "cmake configuration failed."

    cmake --build "$build_dir/build" -j"$(nproc)" \
        >> "$LOG_FILE" 2>&1 || die "llama-server build failed."

    $SUDO install -m 755 "$build_dir/build/bin/llama-server" "${OPT_PREFIX}/bin/llama-server" \
        >> "$LOG_FILE" 2>&1 || die "Failed to install llama-server binary."

    # Install any shared libs produced alongside llama-server
    find "$build_dir/build" -name "*.so*" | while read -r lib; do
        $SUDO install -m 755 "$lib" "${OPT_PREFIX}/lib/" >> "$LOG_FILE" 2>&1 || true
    done
    $SUDO ldconfig >> "$LOG_FILE" 2>&1 || true

    success "llama-server built and installed to ${OPT_PREFIX}/bin/llama-server"
}

# Check if llama-server is present AND actually works (shared libs loaded)
LLAMA_OK=false
if command -v llama-server &>/dev/null; then
    if llama-server --version >> "$LOG_FILE" 2>&1; then
        LLAMA_OK=true
        success "llama-server: $(llama-server --version 2>&1 | head -1)"
    else
        warn "llama-server found but failed to run (missing shared libraries). Rebuilding..."
        $SUDO ldconfig >> "$LOG_FILE" 2>&1 || true
        # Retry after ldconfig
        if llama-server --version >> "$LOG_FILE" 2>&1; then
            LLAMA_OK=true
            success "llama-server: OK (fixed with ldconfig)"
        fi
    fi
fi

if [[ "$LLAMA_OK" == false ]]; then
    warn "llama-server not functional — building from source."
    install_llamacpp
fi

# ── Clone / Update Repository ─────────────────────────────────────────────────

step "Installing INCEPT.sh"

if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Existing installation found — updating..."
    $SUDO git -C "$INSTALL_DIR" pull --ff-only >> "$LOG_FILE" 2>&1 \
        || warn "git pull failed — continuing with existing version."
    success "Repository updated."
else
    log "Cloning repository to ${INSTALL_DIR}..."
    $SUDO git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 \
        || die "Failed to clone INCEPT.sh repository."
    success "Repository cloned."
fi

# ── Python Virtual Environment ────────────────────────────────────────────────

step "Setting up Python environment"

VENV_DIR="${INSTALL_DIR}/.venv"

# Check if existing venv is functional (not just that the dir exists)
VENV_OK=false
if [[ -f "${VENV_DIR}/bin/python3" ]]; then
    if "${VENV_DIR}/bin/python3" -c "import sys" &>/dev/null 2>&1; then
        if "${VENV_DIR}/bin/python3" -m pip --version &>/dev/null 2>&1; then
            VENV_OK=true
        fi
    fi
fi

if [[ "$VENV_OK" == false ]]; then
    if [[ -d "$VENV_DIR" ]]; then
        log "Existing venv is broken — removing and recreating..."
        $SUDO rm -rf "$VENV_DIR"
    fi
    log "Creating virtual environment..."
    $SUDO "$PYTHON" -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1 \
        || die "Failed to create virtual environment. Try: sudo apt install python$(${PYTHON} -c 'import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")')-venv"
    success "Virtual environment created: ${VENV_DIR}"

    # Bootstrap pip inside the venv if missing
    if ! "${VENV_DIR}/bin/python3" -m pip --version &>/dev/null 2>&1; then
        log "Bootstrapping pip inside venv..."
        $SUDO "${VENV_DIR}/bin/python3" -m ensurepip --upgrade >> "$LOG_FILE" 2>&1 \
            || $SUDO curl -fsSL https://bootstrap.pypa.io/get-pip.py \
               | $SUDO "${VENV_DIR}/bin/python3" >> "$LOG_FILE" 2>&1 \
            || die "Failed to install pip in virtual environment."
    fi
else
    success "Virtual environment OK: ${VENV_DIR}"
fi

VENV_PYTHON="${VENV_DIR}/bin/python3"
VENV_PIP="${VENV_DIR}/bin/pip"

log "Upgrading pip..."
$SUDO "$VENV_PYTHON" -m pip install --upgrade pip --quiet >> "$LOG_FILE" 2>&1 \
    || warn "pip upgrade failed — continuing."

log "Installing INCEPT.sh Python package..."
$SUDO "$VENV_PIP" install --quiet -e "${INSTALL_DIR}[cli]" >> "$LOG_FILE" 2>&1 \
    || die "Failed to install INCEPT.sh Python dependencies."

# Try to install llama-cpp-python for in-process inference (optional, falls back to llama-server)
log "Installing llama-cpp-python (optional — fallback to llama-server if this fails)..."
$SUDO "$VENV_PIP" install --quiet llama-cpp-python >> "$LOG_FILE" 2>&1 \
    && success "llama-cpp-python installed." \
    || warn "llama-cpp-python not installed — will use llama-server subprocess instead."

success "Python dependencies installed."

# ── Model Download ────────────────────────────────────────────────────────────

step "Setting up model"

$SUDO mkdir -p "$MODEL_DIR"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILENAME}"

if [[ "$OPT_NO_MODEL" == true ]]; then
    warn "Skipping model download (--no-model). Place ${MODEL_FILENAME} in ${MODEL_DIR} manually."
elif [[ -f "$MODEL_PATH" ]]; then
    MODEL_SIZE=$(du -m "$MODEL_PATH" | awk '{print $1}')
    if [[ "$MODEL_SIZE" -lt 700 ]]; then
        warn "Existing model appears incomplete (${MODEL_SIZE}MB). Re-downloading..."
        $SUDO rm -f "$MODEL_PATH"
    else
        success "Model already present: ${MODEL_PATH} (${MODEL_SIZE}MB)"
    fi
fi

if [[ "$OPT_NO_MODEL" == false && ! -f "$MODEL_PATH" ]]; then
    log "Downloading INCEPT.sh model (774MB) from HuggingFace..."
    log "URL: ${MODEL_URL}"

    # HuggingFace LFS requires the Authorization header even for public repos.
    # Users can set HF_TOKEN env var; a built-in read-only token is used as fallback.
    HF_TOKEN="${HF_TOKEN:-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}"

    $SUDO curl -L --progress-bar --retry 3 --retry-delay 5 \
        --continue-at - \
        -H "Authorization: Bearer ${HF_TOKEN}" \
        -o "$MODEL_PATH" \
        "$MODEL_URL" 2>&1 | tee -a "$LOG_FILE" \
        || { $SUDO rm -f "$MODEL_PATH"; die "Model download failed. Check your connection and retry."; }

    MODEL_SIZE=$(du -m "$MODEL_PATH" | awk '{print $1}')
    if [[ "$MODEL_SIZE" -lt 700 ]]; then
        $SUDO rm -f "$MODEL_PATH"
        die "Downloaded model is too small (${MODEL_SIZE}MB) — may be corrupt. Check log: ${LOG_FILE}"
    fi

    success "Model downloaded: ${MODEL_PATH} (${MODEL_SIZE}MB)"
fi

# ── Launcher Script ───────────────────────────────────────────────────────────

step "Installing binary"

LAUNCHER="${INSTALL_DIR}/incept-launcher.sh"

$SUDO tee "$LAUNCHER" > /dev/null << LAUNCHER
#!/usr/bin/env bash
# INCEPT.sh launcher — auto-generated by install.sh
exec "${VENV_DIR}/bin/python3" -c "from incept.cli.main import main; main()" "\$@"
LAUNCHER

$SUDO chmod 755 "$LAUNCHER"

$SUDO mkdir -p "$(dirname "$BIN_LINK")"
$SUDO ln -sf "$LAUNCHER" "$BIN_LINK"

if command -v incept &>/dev/null; then
    success "Binary installed: ${BIN_LINK}"
else
    warn "Binary installed but not on PATH. Add ${OPT_PREFIX}/bin to your PATH:"
    warn "  export PATH=\"\$PATH:${OPT_PREFIX}/bin\""
fi

# ── Permissions ───────────────────────────────────────────────────────────────

step "Setting permissions"

$SUDO chown -R root:root "$INSTALL_DIR" 2>/dev/null || true
$SUDO chmod -R a+rX "$INSTALL_DIR" 2>/dev/null || true
$SUDO chmod 755 "$VENV_DIR/bin/"* 2>/dev/null || true
[[ -f "$MODEL_PATH" ]] && $SUDO chmod 644 "$MODEL_PATH" 2>/dev/null || true

success "Permissions set."

# ── Smoke Test ────────────────────────────────────────────────────────────────

step "Running smoke test"

if command -v incept &>/dev/null; then
    if incept --version >> "$LOG_FILE" 2>&1; then
        success "Smoke test passed: $(incept --version 2>&1)"
    else
        warn "incept --version returned non-zero. Check ${LOG_FILE} for details."
    fi
else
    warn "incept not found on PATH — skipping smoke test."
fi

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}${BOLD}  INCEPT.sh installed successfully.${RESET}"
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${BOLD}Run:${RESET}       incept"
echo -e "  ${BOLD}One-shot:${RESET}  incept -c \"list open ports\""
echo -e "  ${BOLD}Reasoning:${RESET} incept --think"
echo -e "  ${BOLD}Uninstall:${RESET} bash ${INSTALL_DIR}/install.sh --uninstall"
echo ""
echo -e "  ${BOLD}Installed to:${RESET} ${INSTALL_DIR}"
echo -e "  ${BOLD}Model:${RESET}        ${MODEL_PATH}"
echo -e "  ${BOLD}Binary:${RESET}       ${BIN_LINK}"
echo -e "  ${BOLD}Log:${RESET}          ${LOG_FILE}"
echo ""
