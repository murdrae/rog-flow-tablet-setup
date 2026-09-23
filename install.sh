#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== ASUS ROG Flow Tablet Setup Installer ==="

# 1. System & AUR Packages
echo "[1/6] Installing required system and AUR packages..."
sudo pacman -S --needed --noconfirm \
    base-devel git pango cairo libxkbcommon wayland wayland-protocols scdoc \
    iio-sensor-proxy python-evdev

if command -v yay &>/dev/null; then
    yay -S --needed --noconfirm iio-hyprland-git asusctl
else
    echo "Warning: yay not found. Please install iio-hyprland-git and asusctl manually."
fi

# 2. ASUS Daemon Setup & Battery Threshold
echo "[2/6] Configuring ASUS Daemon and 80% battery charging threshold..."
sudo mkdir -p /etc/systemd/system/asusd.service.d
sudo cp "${SCRIPT_DIR}/systemd/system/asusd.service.d/install.conf" /etc/systemd/system/asusd.service.d/install.conf
sudo systemctl daemon-reload
sudo systemctl enable --now asusd || true

if command -v asusctl &>/dev/null; then
    asusctl battery limit 80 || true
fi

# 3. Accelerometer & Auto-Rotation Service
echo "[3/6] Configuring accelerometer and auto-rotation..."
sudo systemctl enable --now iio-sensor-proxy
mkdir -p ~/.config/systemd/user
cp "${SCRIPT_DIR}/systemd/user/iio-hyprland.service" ~/.config/systemd/user/iio-hyprland.service
systemctl --user daemon-reload
systemctl --user enable --now iio-hyprland.service

# 4. Touchscreen Udev Rules & User Group
echo "[4/6] Setting up touchscreen udev permissions..."
sudo cp "${SCRIPT_DIR}/udev/99-touchscreen.rules" /etc/udev/rules.d/99-touchscreen.rules
sudo usermod -aG input "$USER"
sudo udevadm control --reload-rules
sudo udevadm trigger

# 5. Touch Window Drag Daemon (Long-press Header to Move/Swap Windows)
echo "[5/6] Setting up touch window drag daemon..."
mkdir -p ~/.config/hypr
cp "${SCRIPT_DIR}/config/hypr/touch_window_drag.py" ~/.config/hypr/touch_window_drag.py
chmod +x ~/.config/hypr/touch_window_drag.py
cp "${SCRIPT_DIR}/systemd/user/touch-window-drag.service" ~/.config/systemd/user/touch-window-drag.service
systemctl --user daemon-reload
systemctl --user enable --now touch-window-drag.service


# 6. Build and Install Custom Virtual Keyboard
echo "[6/6] Building and installing custom wvkbd-deskintl virtual keyboard..."
BUILD_DIR="$(mktemp -d /tmp/wvkbd-build-XXXXXX)"
git clone --depth 1 https://github.com/jjsullivan5196/wvkbd.git "${BUILD_DIR}"
python3 "${SCRIPT_DIR}/wvkbd/patch_layout.py" "${BUILD_DIR}/layout.deskintl.h"
make -C "${BUILD_DIR}" LAYOUT=deskintl
mkdir -p ~/.local/bin
cp "${BUILD_DIR}/wvkbd-deskintl" ~/.local/bin/wvkbd-deskintl
chmod 755 ~/.local/bin/wvkbd-deskintl
rm -rf "${BUILD_DIR}"

echo "=== Installation Complete! ==="
echo "Note: Remember to add the tablet config snippets from config/hypr/ to ~/.config/hypr/."
echo "      Then run 'hyprctl reload' to activate keybindings."
