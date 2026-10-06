# 🎛️ SamVivan MacroPad v2.5

[![ESP32](https://img.shields.io/badge/Microcontroller-ESP32--C3-red.svg?logo=espressif)](https://www.espressif.com/)
[![Connectivity](https://img.shields.io/badge/Connectivity-BLE%20HID%20%7C%20USB--Serial-blue.svg)](https://github.com/)
[![Docker](https://img.shields.io/badge/Homelab-Docker%20%7C%20Compose-2496ED.svg?logo=docker)](https://www.docker.com/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20Ubuntu%20%7C%20Cross--Platform-E95420.svg?logo=ubuntu)](https://ubuntu.com/)
[![WebSerial](https://img.shields.io/badge/WebSerial-Chrome%20%2F%20Brave%20Ready-green.svg)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API)

**SamVivan MacroPad v2.5** adalah perangkat macropad mekanikal nirkabel 8-tombol berbasis **ESP32-C3 SuperMini** dengan konektivitas **Bluetooth Low Energy (BLE HID)** dan **USB Serial**. Dilengkapi dengan antarmuka web konfigurator mandiri (*self-hosted studio*) yang dapat dijalankan di **Homelab menggunakan Docker**, serta dukungan penuh untuk **Linux (terutama Ubuntu)**.

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
- **Web Studio & Configurator (Dockerized)**:
  - Tampilan visual chassis 8 tombol mekanikal interaktif.
  - **Web Serial API**: Hubungkan macropad ke browser langsung via USB tanpa perlu install driver tambahan.
  - **Live Hardware Event Monitor**: Menampilkan animasi tombol tertekan di layar secara real-time saat saklar fisik ditekan.
  - Export & Import profil pemetaan tombol (`.json`).
- **Dukungan Native Linux Ubuntu**:
  - Siap dihubungkan via BLE Keyboard atau kabel USB Serial.
  - Cocok diintegrasikan dengan shell script bash, D-Bus, dan webhook Home Assistant.

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

## 🐳 Web Configurator & Homelab Deployment (Docker)

Di dalam repositori ini terdapat web aplikasi mandiri untuk visualisasi dan konfigurasi macropad.

```
macropadv2.5/
├── macropadv2.5.ino         # Firmware Arduino / ESP32-C3
├── README.md                # Dokumentasi utama repositori
└── web-configurator/        # Web App & Docker Configuration
    ├── Dockerfile           # Multi-arch Nginx Alpine image (~20MB)
    ├── docker-compose.yml   # Homelab deployment compose file
    ├── nginx.conf           # Konfigurasi Nginx dengan Gzip
    ├── index.html           # Visual layout & UI Key Inspector
    ├── style.css            # Dark theme & tactile switch styling
    ├── app.js               # Web Serial API & Hardware Event Engine
    └── README.md            # Dokumentasi web-configurator
```

### Menjalankan di Homelab (Docker Compose)
```bash
cd web-configurator
docker compose up -d --build
```
Aplikasi web dapat langsung diakses di: **`http://<IP_HOMELAB>:8080`**

### Menjalankan Lokal di Ubuntu (Tanpa Docker)
```bash
cd web-configurator
python3 -m http.server 8080
```
Buka browser **Google Chrome** atau **Brave** di `http://localhost:8080`.

---

## 🐧 Konfigurasi di Linux Ubuntu

### 1. Izin Akses USB Serial (Web Serial API)
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
