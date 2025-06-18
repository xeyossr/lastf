#!/usr/bin/env bash

set -euo pipefail

PROJECT_NAME="lastf"
VENV_DIR=".venv"
DIST_DIR="${PROJECT_NAME}.dist"
INSTALL_DIR="/opt/lastf"
LAUNCHER_PATH="/usr/bin/lastf"

if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if ! python -m nuitka --version &>/dev/null; then
    echo "[+] Installing Nuitka..."
    pip install -U pip
    pip install nuitka
fi

if [ -f requirements.txt ]; then
    echo "[+] Checking required packages..."
    MISSING_PACKAGES=0
    while IFS= read -r package; do
        pkg_name=$(echo "$package" | cut -d= -f1 | cut -d'<' -f1 | cut -d'>' -f1)
        if ! pip show "$pkg_name" &>/dev/null; then
            echo "[-] Missing: $pkg_name"
            MISSING_PACKAGES=1
        fi
    done < <(grep -vE '^\s*#|^\s*$' requirements.txt)

    if [ "$MISSING_PACKAGES" -eq 1 ]; then
        echo "[+] Installing missing packages from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "[✓] All required packages are already installed."
    fi
fi

echo "[+] Compiling with Nuitka..."
python -m nuitka \
    --standalone \
    --enable-plugin=pylint-warnings \
    --lto=yes \
    --clang \
    --jobs=4 \
    "${PROJECT_NAME}.py"

echo "[+] Installing to ${INSTALL_DIR}..."
sudo rm -rf "$INSTALL_DIR"
sudo mv "$DIST_DIR" "$INSTALL_DIR"

echo "[+] Creating launcher at ${LAUNCHER_PATH}..."
sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/usr/bin/env bash
exec "${INSTALL_DIR}/${PROJECT_NAME}.bin" "\$@"
EOF
sudo chmod +x "$LAUNCHER_PATH"

echo "[✓] Build complete. Run it with: lastf"
