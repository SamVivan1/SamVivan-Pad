#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
ICONS_BASE="$HOME/.local/share/icons/hicolor"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"

echo "================================================================"
echo " 🎛️  Installing SamVivan MacroPad (Native Linux Desktop App)"
echo "================================================================"

# 1. Make sure the scripts are executable
echo "[1/7] Setting executable file permissions..."
chmod +x "$SCRIPT_DIR/run.sh" "$SCRIPT_DIR/main.py" "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/uninstall.sh"

# 2. Stop and clean up the old systemd daemon if it still exists
echo "[2/7] Cleaning up leftover background daemon..."
systemctl --user stop samvivan-macropad 2>/dev/null || true
systemctl --user disable samvivan-macropad 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/samvivan-macropad.service"
systemctl --user daemon-reload 2>/dev/null || true

# 3. Ensure Python dependencies (PyGObject/dbus are distro packages)
echo "[3/7] Checking Python dependencies (pyserial)..."
if ! /usr/bin/python3 -c "import serial" 2>/dev/null; then
    /usr/bin/python3 -m pip install --user --break-system-packages pyserial \
        || /usr/bin/python3 -m pip install --user pyserial \
        || echo "   !! Failed to install pyserial — USB serial will be unavailable."
fi

# 4. Generate multi-resolution PNG icons if not already present
echo "[4/7] Preparing multi-resolution application icons..."
python3 -c "
import os
from PIL import Image

src_png = os.path.join('$SCRIPT_DIR', 'samvivan-macropad.png')
if not os.path.exists(src_png):
    import subprocess
    subprocess.run(['inkscape', '-w', '512', '-h', '512', os.path.join('$SCRIPT_DIR', 'samvivan-macropad.svg'), '-o', src_png], check=True)

img = Image.open(src_png)
sizes = [48, 64, 128, 256, 512]
base_dir = os.path.expanduser('$ICONS_BASE')

for s in sizes:
    target_dir = os.path.join(base_dir, f'{s}x{s}', 'apps')
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, 'samvivan-macropad.png')
    resized = img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(target_path, 'PNG')

# Pixmaps fallback
pixmaps = os.path.expanduser('$PIXMAPS_DIR')
os.makedirs(pixmaps, exist_ok=True)
img.save(os.path.join(pixmaps, 'samvivan-macropad.png'), 'PNG')
"

# Install scalable SVG
mkdir -p "$ICONS_BASE/scalable/apps" "$PIXMAPS_DIR"
cp "$SCRIPT_DIR/samvivan-macropad.svg" "$ICONS_BASE/scalable/apps/samvivan-macropad.svg"
cp "$SCRIPT_DIR/samvivan-macropad.svg" "$PIXMAPS_DIR/samvivan-macropad.svg"

# Install tray icons (white logo, 3 statuses like Nextcloud) into the icon theme so
# the Ubuntu panel snapshot can find them (the panel resolver uses the icon theme,
# not the helper's search path). Icon names: samvivan-macropad-tray,
# samvivan-macropad-tray-checking, samvivan-macropad-tray-off.
TRAY_ICON_DIR="$SCRIPT_DIR/tray-icons/hicolor"
if [ -d "$TRAY_ICON_DIR" ]; then
    echo "   -> Installing tray icons (3 statuses: connected/searching/disconnected)..."
    for size_dir in "$TRAY_ICON_DIR"/*x*; do
        size=$(basename "$size_dir")
        mkdir -p "$ICONS_BASE/$size/apps"
        cp "$size_dir/apps/"*.png "$ICONS_BASE/$size/apps/" 2>/dev/null || true
    done
    mkdir -p "$ICONS_BASE/scalable/apps"
    cp "$TRAY_ICON_DIR/scalable/apps/"*.svg "$ICONS_BASE/scalable/apps/" 2>/dev/null || true
    # Do not create index.theme in ~/.local/share/icons/hicolor: it can shadow the
    # system hicolor index.theme and make other icons fall back.
    # GTK/Shell still find the icons without a cache file.
    rm -f "$ICONS_BASE/index.theme"
fi

# 5. Create and install the .desktop file + autostart entry
echo "[5/7] Installing launcher into the Ubuntu Application Menu..."
mkdir -p "$APPS_DIR"
# The .desktop file name MUST match the Gtk application_id (com.samvivan.macropad)
# so GNOME dock/menu matches the running application with its icon.
rm -f "$APPS_DIR/samvivan-macropad.desktop"
cat > "$APPS_DIR/com.samvivan.macropad.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SamVivan MacroPad
GenericName=MacroPad Peripheral Manager
Comment=Configure keys, actions, and profiles for SamVivan MacroPad
Exec=$SCRIPT_DIR/run.sh
Icon=samvivan-macropad
Terminal=false
Categories=Utility;HardwareSettings;Settings;
StartupWMClass=com.samvivan.macropad
Keywords=macropad;keyboard;macro;hardware;peripheral;samvivan;
EOF
chmod +x "$APPS_DIR/com.samvivan.macropad.desktop"
touch "$APPS_DIR/com.samvivan.macropad.desktop"

# Autostart: launch in the background at login (tray only, no window).
echo "   -> Installing autostart entry (runs in background/tray)..."
mkdir -p "$AUTOSTART_DIR"
rm -f "$AUTOSTART_DIR/samvivan-macropad.desktop"
cat > "$AUTOSTART_DIR/com.samvivan.macropad.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SamVivan MacroPad
GenericName=MacroPad Peripheral Manager
Comment=Start SamVivan MacroPad in the background (tray)
Exec=$SCRIPT_DIR/run.sh --hidden
Icon=samvivan-macropad
Terminal=false
StartupWMClass=com.samvivan.macropad
X-GNOME-Autostart-enabled=true
EOF
chmod +x "$AUTOSTART_DIR/com.samvivan.macropad.desktop"

# 6. Refresh the icon cache and desktop database
echo "[6/7] Refreshing icon theme cache & desktop database..."
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

# 7. Check USB serial port permissions
echo "[7/7] Checking USB dialout port permissions..."
if ! groups "$USER" | grep -q '\bdialout\b'; then
    echo " -> Adding user $USER to the dialout group..."
    sudo usermod -a -G dialout "$USER" || true
    echo "    (Note: you may need to log out & back in to apply USB permissions)"
else
    echo " -> User already has dialout access."
fi

echo "================================================================"
echo " ✅ SUCCESS! SamVivan MacroPad and its icons have been installed successfully."
echo ""
echo " 💡 Try opening the Application Menu (Super Key) and typing 'SamVivan MacroPad'."
echo "================================================================"
