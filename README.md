# 🎛️ SamVivan MacroPad v2.5

[![ESP32](https://img.shields.io/badge/Microcontroller-ESP32--C3-red.svg?logo=espressif)](https://www.espressif.com/)
[![Connectivity](https://img.shields.io/badge/Connectivity-BLE%20HID%20%7C%20USB--Serial-blue.svg)](https://github.com/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20Ubuntu%20%7C%20Cross--Platform-E95420.svg?logo=ubuntu)](https://ubuntu.com/)

**SamVivan MacroPad v2.5** adalah perangkat macropad mekanikal nirkabel 8-tombol berbasis **ESP32-C3 SuperMini** dengan konektivitas **Bluetooth Low Energy (BLE HID)** dan **USB Serial**. Dilengkapi **aplikasi desktop native Linux (GTK4 + Libadwaita)** untuk konfigurasi tombol, monitor event hardware, dan integrasi **Home Assistant** — tanpa server web, tanpa Docker.

---

## ✨ Fitur Utama

- **8 Tombol Mekanikal Multi-Trigger**:
  - **Single Click (1x)**: Eksekusi shortcut standar respons instan.
  - **Double Click (2x)**: Deteksi klik ganda dengan umpan balik LED berkedip 2 kali.
  - **Hold / Long Press (HOLD)**: Tahan tombol > 450ms dengan umpan balik LED berkedip 3 kali.
- **Dual Layer / Mode Switcher**:
  - **Desktop Mode**: Shortcut harian, navigasi, dan produktivitas OS (LED Status ON).
  - **Home Assistant Mode**: Shortcut IoT dan otomasi smart home (LED Status OFF).
- **Tombol Khusus Sistem (B1 / GPIO 20)**:
  - Single Click: Toggle layer (*Desktop Mode* ↔ *Home Assistant Mode*).
  - Hold / Long Press: Mengetik passcode/string otomatis (`031004`).
- **Aplikasi Desktop Native (GTK4 + Libadwaita)**:
  - Tampilan visual chassis 8 tombol mekanikal interaktif dengan inspector aksi per trigger (1x / 2x / hold).
  - **Live Hardware Event Monitor**: animasi tombol tertekan di layar secara real-time saat saklar fisik ditekan.
  - **Console Serial**: log hardware + kirim perintah ke macropad dari dalam aplikasi.
  - Halaman **Profil**: simpan, impor & ekspor profil pemetaan tombol (`.json`) + preset bawaan.
  - Pill status **Serial** dan **Home Assistant** langsung di header.
- **Dukungan Native Linux Ubuntu**:
  - Siap dihubungkan via BLE Keyboard atau kabel USB Serial.
  - **Aplikasi desktop native** (GTK4 + Libadwaita) — layaknya Vial / OpenRGB, bukan daemon background.
  - Pemindai aplikasi `.desktop` Ubuntu + peluncur tombol tanpa perlu ngedit script.
  - **Home Assistant Native**: panggil service HA (`light.toggle`, `automation.trigger`, ...)
    langsung dari aplikasi via REST API — tanpa bash script, tanpa `curl`.
  - Fallback ke mode webhook & bash script bila tetap dibutuhkan.

---

## 📌 Spesifikasi Hardware & Pinout

Menggunakan mikrokontroler **ESP32-C3 SuperMini** dengan konfigurasi saklar aktif rendah (*Active-LOW / Internal Pull-Up*):

| Komponen | Pin Fisik (GPIO) | Fungsi Bawaan | Keterangan |
| :--- | :---: | :--- | :--- |
| **Status LED** | `GPIO 4` | Indikator Mode & Feedback Blink | ON = Desktop Mode, OFF = HA Mode |
| **Button 1** | `GPIO 20` | Mode Switch / Passcode String | Single: Toggle Mode, Hold: String `"031004"` |
| **Button 2** | `GPIO 9` | Macro 1 | Desktop: Ctrl+Alt+Shift + 2 / Q / A |
| **Button 3** | `GPIO 2` | Macro 2 | Desktop: Ctrl+Alt+Shift + 3 / W / S |
| **Button 4** | `GPIO 1` | Macro 3 | Desktop: Ctrl+Alt+Shift + 4 / E / D |
| **Button 5** | `GPIO 21` | Macro 4 | Desktop: Ctrl+Alt+Shift + 5 / I / F |
| **Button 6** | `GPIO 10` | Macro 5 | Desktop: Ctrl+Alt+Shift + 6 / T / G |
| **Button 7** | `GPIO 3` | Macro 6 | Desktop: Ctrl+Alt+Shift + 7 / Y / H |
| **Button 8** | `GPIO 0` | Macro 7 | Desktop: Ctrl+Alt+Shift + 8 / U / J |

### ⏱️ Parameter Waktu (Timing Engine)
* **Debounce Filter**: `25 ms` (Penyaring getaran mekanis saklar switch)
* **Click Timeout**: `250 ms` (Jeda maksimal antar ketukan untuk deteksi klik ganda)
* **Hold Timeout**: `450 ms` (Durasi penekanan untuk memicu aksi Long Press)

---

## 🗺️ Pemetaan Default (Keymap Layers)

Semua shortcut bawaan dikirimkan dengan kombinasi tombol pengubah: `Ctrl + Alt + Shift + <Key>`

### 1. Desktop Mode (LED GPIO 4: ON)
| Tombol | Single Click (1x) | Double Click (2x) | Hold / Long Press |
| :---: | :---: | :---: | :---: |
| **B1** | *Toggle ke HA Mode* | *None* | Teks: `"031004"` |
| **B2** | `Key 2` | `Key Q` | `Key A` |
| **B3** | `Key 3` | `Key W` | `Key S` |
| **B4** | `Key 4` | `Key E` | `Key D` |
| **B5** | `Key 5` | `Key I` | `Key F` |
| **B6** | `Key 6` | `Key T` | `Key G` |
| **B7** | `Key 7` | `Key Y` | `Key H` |
| **B8** | `Key 8` | `Key U` | `Key J` |

### 2. Home Assistant Mode (LED GPIO 4: OFF)
| Tombol | Single Click (1x) | Double Click (2x) | Hold / Long Press |
| :---: | :---: | :---: | :---: |
| **B1** | *Toggle ke Desktop Mode* | *None* | Teks: `"031004"` |
| **B2** | `Key F2` | `Key Z` | `Key 9` |
| **B3** | `Key F3` | `Key X` | `Key 0` |
| **B4** | `Key F4` | `Key C` | `Key I` |
| **B5** | `Key F5` | `Key V` | `Key O` |
| **B6** | `Key F6` | `Key B` | `Key P` |
| **B7** | `Key F7` | `Key N` | `Key K` |
| **B8** | `Key F8` | `Key P` | `Key L` |

---

## 📁 Struktur Repositori

```
macropadv2.5/
├── macropadv2.5.ino          # Firmware Arduino / ESP32-C3
├── README.md                 # Dokumentasi utama repositori
└── linux-app/                # Aplikasi desktop native GTK4 + Libadwaita
    ├── main.py               # Entry point Adw.Application
    ├── config.py             # Profil, preset, validasi konfigurasi
    ├── state.py              # Bus state runtime (tanpa GTK)
    ├── ui/                   # Halaman & dialog GTK4
    │   ├── window.py         # Jendela utama (sidebar + stack halaman)
    │   ├── keys_page.py      # Grid 8 keycap + inspector aksi
    │   ├── action_editor.py  # Editor aksi per trigger (1x / 2x / hold)
    │   ├── console_page.py   # Console serial (log + kirim perintah)
    │   ├── settings_page.py  # Halaman Profil & Pengaturan
    │   ├── ha_dialogs.py     # Dialog koneksi HA & Entity Picker
    │   ├── app_picker.py     # Pemilih aplikasi (.desktop)
    │   └── css.py            # Gaya kustom mengikuti HIG GNOME
    ├── app_scanner.py        # Pemindai aplikasi terpasang (.desktop)
    ├── system_actions.py     # Eksekusi aksi lokal (shortcut, audio, teks, ...)
    ├── home_assistant.py     # Klien REST Home Assistant (dipanggil langsung)
    ├── serial_listener.py    # Listener serial + dispatcher aksi
    ├── samvivan-macropad.svg # Ikon vector resmi aplikasi
    ├── samvivan-macropad.desktop # Entry menu aplikasi Ubuntu
    ├── run.sh                # Launcher script aplikasi
    ├── install.sh            # Pasang ke Menu Aplikasi Ubuntu (Super Key)
    ├── uninstall.sh          # Hapus aplikasi & shortcut secara bersih
    └── README.md             # Dokumentasi aplikasi native
```

### 💻 Menjalankan sebagai Aplikasi Native Linux (Direkomendasikan)
Aplikasi ini berjalan layaknya software peripheral modern (**Vial, Piper, Razer Synapse, OpenRGB**), bukan daemon yang membebani background:
1. **Pasang ke Menu Aplikasi Ubuntu**:
   ```bash
   cd linux-app
   ./install.sh
   ```
2. Tekan tombol **Super / Windows** di keyboard, ketik **`SamVivan MacroPad`**, dan klik aplikasinya! Jendela native GTK4 akan terbuka.
3. Atau jalankan langsung dari terminal:
   ```bash
   cd linux-app
   ./run.sh
   ```
4. Saat jendela ditutup, aplikasi akan berhenti secara bersih tanpa meninggalkan proses background.

Halaman aplikasi:
- **Tombol** — grid 8 keycap, switch mode Desktop / Home Assistant, dan inspector aksi per trigger.
- **Console Serial** — log hardware real-time + input kirim perintah ke macropad.
- **Profil** — simpan / impor / ekspor profil JSON + preset bawaan.
- **Pengaturan** — parameter timing (debounce / click / hold), koneksi Home Assistant, dan pindai ulang aplikasi.

### 🏠 Koneksi Home Assistant Native (Scriptless)
Semua aksi tombol bertipe **Home Assistant (Native)** dieksekusi langsung oleh aplikasi
ke `POST /api/services/<domain>/<service>` — menggantikan script `ha-*.sh` lama.
Tidak ada IP, token, atau entity yang di-hardcode di source:
1. Buka aplikasi → klik pill **`HA: ...`** di header (atau **Koneksi** di Key Inspector).
   Dialog langsung terbuka — status dibaca dari cache, cek live jalan di latar belakang.
2. Isi URL HA + **Long-Lived Access Token** (HA → Profile → Security → Long-Lived Access Tokens).
3. **Test Koneksi** → **Simpan Koneksi** → sistem otomatis memindai semua entity interaktif
   dan membuka **Entity Picker** (pilih HA, lalu pilih entity → tempel ke tombol).
4. Pilih service (`toggle`, `turn_on`, `trigger`, `press`, ...), lalu **Test** untuk eksekusi.
5. Token tersimpan di `~/.config/samvivan-macropad/ha_config.json`
   (fallback baca: `~/.config/home-assistant/env`); hasil scan entity di-cache di
   `~/.config/samvivan-macropad/ha_entities_cache.json` sehingga tetap tampil saat HA offline.
6. Semua pemanggilan dilakukan langsung dari modul Python `home_assistant.py` —
   tidak ada endpoint HTTP lokal maupun layanan tambahan yang berjalan di background.

### 🗑️ Cara Uninstall dari Ubuntu
Untuk menghapus shortcut dan ikon aplikasi dari sistem Ubuntu:
```bash
cd linux-app
./uninstall.sh
```

---

## 🐧 Konfigurasi di Linux Ubuntu

### 1. Izin Akses USB Serial
Agar browser di Ubuntu memiliki izin membaca port serial mikrokontroler:
```bash
# Tambahkan user Anda ke group dialout
sudo usermod -a -G dialout $USER

# Berikan izin ke port ttyUSB atau ttyACM
sudo chmod a+rw /dev/ttyUSB0    # atau /dev/ttyACM0
```
*(Setelah menjalankan perintah di atas, lakukan logout lalu login kembali agar grup aktif).*

### 2. Pairing Bluetooth BLE di Ubuntu
1. Hidupkan Bluetooth pada PC Ubuntu Anda.
2. Nyalakan ESP32 Macropad.
3. Buka **Settings -> Bluetooth** di Ubuntu.
4. Cari perangkat bernama **`SamVivan MacroPad`**, lalu klik **Connect**.

---

## 🛠️ Flashing Firmware ke ESP32

1. Buka Arduino IDE.
2. Tambahkan URL Board ESP32 jika belum ada:
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Pilih board: **ESP32C3 Dev Module** (atau sesuai board ESP32-C3 yang Anda gunakan).
4. Install library yang dibutuhkan:
   - `HijelHID_BLEKeyboard` (atau `ESP32-BLE-Keyboard`)
5. Buka file [`macropadv2.5.ino`](macropadv2.5.ino).
6. Tancapkan kabel USB-C ke ESP32 dan klik **Upload**.

---

## 👤 Penulis & Lisensi

Dibuat oleh **SamVivan**.
Proyek ini bersifat open-source di bawah lisensi MIT. Silakan fork, modifikasi, dan sesuaikan dengan setup homelab Anda!
