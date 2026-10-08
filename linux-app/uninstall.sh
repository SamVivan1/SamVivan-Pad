#!/usr/bin/env bash
set -e

APPS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
ICONS_BASE="$HOME/.local/share/icons/hicolor"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "================================================================"
echo " 🗑️  Uninstalling SamVivan MacroPad Desktop App & Components"
echo "================================================================"

# 1. Stop and remove the systemd service if it still exists
echo "[1/4] Checking and stopping the background service..."
if systemctl --user is-active --quiet samvivan-macropad 2>/dev/null; then
    echo " -> Stopping service samvivan-macropad..."
    systemctl --user stop samvivan-macropad 2>/dev/null || true
fi
systemctl --user disable samvivan-macropad 2>/dev/null || true
rm -f "$SYSTEMD_USER_DIR/samvivan-macropad.service"
systemctl --user daemon-reload 2>/dev/null || true
echo " -> Background service cleaned up successfully."

# 2. Remove the desktop shortcut and autostart files
echo "[2/4] Removing the application menu shortcut and autostart entry..."
rm -f "$APPS_DIR/samvivan-macropad.desktop" "$APPS_DIR/com.samvivan.macropad.desktop"
rm -f "$AUTOSTART_DIR/samvivan-macropad.desktop" "$AUTOSTART_DIR/com.samvivan.macropad.desktop"

# 3. Remove all application icon variations
echo "[3/4] Removing multi-resolution application icons..."
for s in 48 64 128 256 512; do
    rm -f "$ICONS_BASE/${s}x${s}/apps/samvivan-macropad.png"
done
rm -f "$ICONS_BASE/scalable/apps/samvivan-macropad.svg"
rm -f "$PIXMAPS_DIR/samvivan-macropad.png"
rm -f "$PIXMAPS_DIR/samvivan-macropad.svg"

# 4. Refresh the icon & desktop cache
echo "[4/4] Refreshing the application & icon cache..."
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo "================================================================"
echo " ✅ SUCCESS! SamVivan MacroPad has been cleanly removed from the Ubuntu system."
echo ""
echo " Note: Your profile & key configuration files at:"
echo "   $HOME/.config/samvivan-macropad/"
echo " are kept in case you want to use them again later."
echo " To remove everything including the configuration, run:"
echo "   rm -rf $HOME/.config/samvivan-macropad"
echo "================================================================"
