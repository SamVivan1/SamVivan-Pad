#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS_DIR="$HOME/.local/share/applications"
ICONS_BASE="$HOME/.local/share/icons/hicolor"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"

echo "================================================================"
echo " 🎛️  Installing SamVivan MacroPad (Native Linux Desktop App)"
echo "================================================================"

# 1. Pastikan script dapat dieksekusi
echo "[1/6] Mengatur perizinan berkas eksekusi..."
chmod +x "$SCRIPT_DIR/run.sh" "$SCRIPT_DIR/main.py" "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/uninstall.sh"

# 2. Hentikan dan bersihkan daemon systemd lama jika masih ada
echo "[2/6] Membersihkan sisa daemon background lama..."
systemctl --user stop samvivan-macropad 2>/dev/null || true
systemctl --user disable samvivan-macropad 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/samvivan-macropad.service"
systemctl --user daemon-reload 2>/dev/null || true

# 3. Generate multi-resolution PNG icons jika belum ada
echo "[3/6] Menyiapkan ikon aplikasi multi-resolusi..."
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

# Pasang SVG scalable
mkdir -p "$ICONS_BASE/scalable/apps" "$PIXMAPS_DIR"
cp "$SCRIPT_DIR/samvivan-macropad.svg" "$ICONS_BASE/scalable/apps/samvivan-macropad.svg"
cp "$SCRIPT_DIR/samvivan-macropad.svg" "$PIXMAPS_DIR/samvivan-macropad.svg"

# 4. Buat dan pasang file .desktop
echo "[4/6] Memasang launcher ke Menu Aplikasi Ubuntu..."
mkdir -p "$APPS_DIR"
cat > "$APPS_DIR/samvivan-macropad.desktop" <<EOF
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
StartupWMClass=samvivan-macropad
Keywords=macropad;keyboard;macro;hardware;peripheral;samvivan;
EOF
chmod +x "$APPS_DIR/samvivan-macropad.desktop"
touch "$APPS_DIR/samvivan-macropad.desktop"

# 5. Refresh cache ikon dan desktop database
echo "[5/6] Memperbarui cache icon theme & desktop database..."
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

# 6. Periksa izin serial port USB
echo "[6/6] Memeriksa izin port USB dialout..."
if ! groups "$USER" | grep -q '\bdialout\b'; then
    echo " -> Menambahkan user $USER ke grup dialout..."
    sudo usermod -a -G dialout "$USER" || true
    echo "    (Catatan: Anda mungkin perlu logout & login kembali untuk menerapkan izin USB)"
else
    echo " -> User sudah memiliki akses dialout."
fi

echo "================================================================"
echo " ✅ SUKSES! SamVivan MacroPad dan ikonnya telah terpasang sempurna."
echo ""
echo " 💡 Coba buka Menu Aplikasi (Super Key) dan ketik 'SamVivan MacroPad'."
echo "================================================================"
