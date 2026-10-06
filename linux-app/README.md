# 🎛️ SamVivan MacroPad - Native Linux Desktop Application

Aplikasi desktop native untuk Linux Ubuntu (seperti **Razer Synapse, Logitech G Hub, Vial, Piper, atau OpenRGB**),
dibangun dengan **GTK4 + Libadwaita** (HIG GNOME).

Aplikasi ini **bukan daemon yang terus berjalan di background**, melainkan aplikasi desktop mandiri:
* Muncul di **Menu Aplikasi Ubuntu** (Dash / App Launcher).
* Membuka jendela aplikasi native GTK4 dengan akselerasi hardware.
* Memindai aplikasi terpasang di sistem Ubuntu secara otomatis (file `.desktop`).
* Memungkinkan konfigurasi tombol, aksi shortcut, peluncur aplikasi, dan otomasi audio.
* Listener serial berjalan di dalam proses yang sama — eksekusi aksi langsung dari Python,
  tanpa server HTTP lokal.
* Saat jendela ditutup, seluruh proses aplikasi berhenti dengan bersih.

---

## 📖 Halaman Aplikasi

| Halaman | Isi |
| :--- | :--- |
| **Tombol** | Grid 8 keycap visual (index, GPIO, label, 3 chip trigger), switch mode *Desktop / Home Assistant*, dan inspector aksi per trigger (Single, Double, Hold). |
| **Console Serial** | Log hardware real-time dengan pewarnaan + input untuk mengirim perintah ke macropad. |
| **Profil** | Simpan (Ctrl+S), impor & ekspor profil JSON, dan terapkan preset bawaan. |
| **Pengaturan** | Parameter timing (debounce / click / hold), koneksi Home Assistant, pindai ulang aplikasi, dan info aplikasi. |

Juga tersedia di header: pill **Serial** (klik → buka console), pill **HA** (klik → dialog koneksi),
dan tombol **Simpan**.

---

## 🚀 Instalasi ke Menu Aplikasi Ubuntu

Untuk memasang aplikasi ke menu aplikasi Ubuntu (lengkap dengan ikon dan shortcut desktop):

```bash
cd /home/samvivan/Arduino/samvivanpad/macropadv2.5/linux-app
./install.sh
```

Setelah diinstall, Anda cukup:
1. Tekan tombol **Super / Windows** pada keyboard Anda.
2. Ketik **"SamVivan MacroPad"**.
3. Klik ikon aplikasi untuk membukanya.

---

## 💻 Menjalankan Langsung via Terminal

Anda juga dapat menjalankan aplikasi langsung dari terminal:
```bash
./run.sh
```
atau:
```bash
python3 main.py
```

---

## 🏠 Integrasi Home Assistant Native (Tanpa Script)

Aplikasi memanggil Home Assistant langsung lewat **REST API** — tidak ada lagi
`bash script`, `curl`, atau `notify-send` wrapper seperti
`~/device-tweak/macropad/scripts/ha-*.sh`.

Cara kerjanya:
1. Buka aplikasi, lalu klik pill **`HA: ...`** di header (atau tombol **Koneksi** pada aksi
   *Home Assistant (Native)* di Key Inspector). Dialog terbuka **seketika** — status dibaca
   dari cache, cek live dilakukan di latar belakang.
2. Isi **Home Assistant URL** (`http://<ip>:8123`) dan **Long-Lived Access Token**
   (HA → Profile → Security → Long-Lived Access Tokens → Create).
3. Klik **Test Koneksi**, lalu **Simpan Koneksi** — sistem otomatis memindai semua entity
   interaktif (light, switch, cover, media_player, dsb.) dari `/api/states`.
4. **Entity Picker** terbuka: cari / filter per domain, lalu klik entity untuk dipasang
   ke tombol yang sedang diedit.
5. Pada aksi tombol, pilih service (`toggle`, `turn_on`, `trigger`, `press`, ...),
   lalu klik **Test** untuk mengeksekusinya langsung.

Detail teknis:
- **Tanpa hardcode**: tidak ada IP, token, atau entity bawaan di kode. Semua URL/token
  berasal dari input pengguna; daftar tombol Home Assistant mode memakai nama generik
  (`HA Key 1` … `HA Key 7`) sampai Anda memilih entity sendiri.
- Kredensial disimpan di `~/.config/samvivan-macropad/ha_config.json`
  (fallback baca: `~/.config/home-assistant/env`, format `HA_URL=` / `HA_TOKEN=`).
- Hasil scan entity di-cache di `~/.config/samvivan-macropad/ha_entities_cache.json`
  sehingga daftar tetap tampil walau HA sedang offline (`live: false`).
- Modul: [`home_assistant.py`](home_assistant.py) (`HomeAssistantClient`) — dipanggil
  **langsung** dari UI dan listener; tidak ada endpoint HTTP lokal yang disiapkan.
- Ikon domain/entity memakai ikon tema GTK/Adwaita dengan fallback otomatis
  (UI bebas emoji).
- Setiap eksekusi aksi HA mengirim notifikasi desktop via `notify-send`.
- Jika HA tidak terjangkau, daftar entity jatuh ke cache terakhir di disk; scan ulang
  otomatis ditahan 30 detik supaya respons UI tetap instan.

---

## 🔌 Console Serial

* Log masuk otomatis dari listener (`[HARDWARE]`, `[ACTION]`, `[TX]`, error).
* Klik pill **Serial** di header untuk menuju console.
* Ketik perintah (mis. `CMD:PING`) lalu **Enter / Kirim** untuk mengirimkannya
  ke macropad melalui port yang sedang terbuka.
* Port dicari otomatis di `/dev/ttyACM*` dan `/dev/ttyUSB*` (115200 Baud),
  auto-reconnect bila kabel dicabut.

---


## ⌨️ Simulasi Shortcut & Teks (Injeksi Keyboard)

Aksi `Shortcut` dan `Ketik Teks` membutuhkan alat simulasi keyboard untuk mengirim input ke jendela aktif.
Karena GNOME Wayland membatasi injeksi input, aplikasi menggunakan urutan prioritas otomatis:

1. `wtype` (direkomendasikan Wayland modern, berbasis wlroots)
2. `ydotool` (uinput, bekerja di sebagian besar session Wayland/GNOME — membutuhkan daemon)
3. `xdotool` (X11 saja)

### Instalasi (Ubuntu)

```bash
# Opsi A – wtype
sudo apt install wtype

# Opsi B – ydotool (rekomendasi GNOME Wayland 44+)
sudo apt install ydotool
# Jalankan daemon uinput
systemctl --user enable --now ydotool
# atau: sudo ydotoold &

# Opsi C – xdotool (hanya untuk X11 / XWayland)
sudo apt install xdotool
```

**Catatan ydotool**: beberapa versi membutuhkan akses uinput; pastikan `ydotoold` berjalan agar shortcut/ketik teks bisa bekerja.


## 🗑️ Cara Uninstall

Untuk menghapus aplikasi dari menu aplikasi Ubuntu dan membersihkan shortcut serta ikon:

```bash
cd /home/samvivan/Arduino/samvivanpad/macropadv2.5/linux-app
./uninstall.sh
```
