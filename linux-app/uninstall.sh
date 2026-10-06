#!/usr/bin/env bash
set -e

APPS_DIR="$HOME/.local/share/applications"
ICONS_BASE="$HOME/.local/share/icons/hicolor"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "================================================================"
echo " 🗑️  Uninstalling SamVivan MacroPad Desktop App & Components"
echo "================================================================"

# 1. Hentikan dan hapus service systemd jika masih ada
echo "[1/4] Memeriksa dan menghentikan background service..."
if systemctl --user is-active --quiet samvivan-macropad 2>/dev/null; then
    echo " -> Menghentikan service samvivan-macropad..."
    systemctl --user stop samvivan-macropad 2>/dev/null || true
fi
systemctl --user disable samvivan-macropad 2>/dev/null || true
rm -f "$SYSTEMD_USER_DIR/samvivan-macropad.service"
systemctl --user daemon-reload 2>/dev/null || true
echo " -> Background service berhasil dibersihkan."

# 2. Hapus file desktop shortcut
echo "[2/4] Menghapus shortcut menu aplikasi Ubuntu..."
rm -f "$APPS_DIR/samvivan-macropad.desktop"

# 3. Hapus seluruh variasi ikon aplikasi
echo "[3/4] Menghapus ikon aplikasi multi-resolusi..."
for s in 48 64 128 256 512; do
    rm -f "$ICONS_BASE/${s}x${s}/apps/samvivan-macropad.png"
done
rm -f "$ICONS_BASE/scalable/apps/samvivan-macropad.svg"
rm -f "$PIXMAPS_DIR/samvivan-macropad.png"
rm -f "$PIXMAPS_DIR/samvivan-macropad.svg"

# 4. Perbarui cache ikon & desktop
echo "[4/4] Memperbarui cache aplikasi & ikon..."
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo "================================================================"
echo " ✅ SUKSES! SamVivan MacroPad telah dihapus bersih dari sistem Ubuntu."
echo ""
echo " Catatan: Berkas profil & konfigurasi tombol Anda di:"
echo "   $HOME/.config/samvivan-macropad/"
echo " masih dipertahankan jika Anda ingin menggunakannya lagi nanti."
echo " Jika ingin menghapus seluruhnya termasuk konfigurasi, jalankan:"
echo "   rm -rf $HOME/.config/samvivan-macropad"
echo "================================================================"
