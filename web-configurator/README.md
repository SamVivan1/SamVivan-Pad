# 🎛️ SamVivan MacroPad Studio (Web Configurator)

Aplikasi Web & Dashboard untuk konfigurasi dan live monitor hardware **SamVivan MacroPad v2.5** (berbasis ESP32-C3 SuperMini dengan BLE HID & 8 tombol mekanikal).

Aplikasi ini dapat di-hosting secara mandiri di **Homelab (Docker)** dan diakses dari browser mana saja (Google Chrome, MS Edge, Chromium, Brave) di Linux Ubuntu.

---

## 🚀 Fitur Utama
1. **Interactive Physical Visualizer**:
   - Tampilan grafis 8 mechanical keycaps (2x4 grid) dengan indikator GPIO fisik (`20, 9, 2, 1, 21, 10, 3, 0`).
   - Indikator LED status (GPIO 4) yang mensimulasikan mode aktif (*Desktop Mode vs Home Assistant Mode*).
2. **Multi-Trigger Configuration**:
   - **Single Click (1x)**: Aksi klik cepat.
   - **Double Click (2x)**: Aksi klik ganda (dengan feedback LED 2x).
   - **Hold / Long Press (HOLD)**: Tahan > 450ms (dengan feedback LED 3x).
3. **Jenis Aksi Tombol**:
   - **Keyboard Shortcut**: Kombinasi modifier (`Ctrl`, `Alt`, `Shift`, `Super/Win`) + tombol (`A-Z`, `0-9`, `F1-F24`, Navigation keys).
   - **Text String / Macro**: Mengetik teks otomatis (contoh passcode `"031004"`, command bash, dsb).
   - **Media Control**: Mute, Volume Up, Volume Down, Play/Pause, Next/Prev Track.
   - **Mode Toggle**: Pindah layer (Desktop Mode ↔ Home Assistant Mode).
4. **Hardware Communication via Web Serial API**:
   - Browser di PC Ubuntu terhubung langsung ke ESP32 via kabel USB Serial tanpa perlu install driver tambahan.
   - **Live Event Monitor**: Melihat log input fisik secara real-time di layar. Saat tombol fisik ditekan, keycap di layar akan ikut menyala dan tertekan secara dinamis!
5. **Profile Management**:
   - Simpan dan muat profil via file JSON (`Export / Import`).
   - Preset bawaan: *Default v2.5*, *Productivity & Ubuntu Shortcuts*, dan *Media & Streaming*.
6. **Home Assistant Native (Scriptless)**:
   - Pill **`HA: ...`** di header → modal koneksi **langsung terbuka** (status dibaca dari
     cache, cek live dilakukan di latar belakang): isi URL + Long-Lived Access Token,
     **Test Koneksi**, **Simpan**, dan **Muat Ulang Entities**.
   - Setelah simpan, **Entity Picker** terbuka otomatis: pencarian, filter per domain,
     status state real-time, lalu klik entity untuk memasangkannya ke tombol.
   - Pada aksi tombol **Home Assistant (Native)**: pilih service (`toggle`, `turn_on`,
     `trigger`, `press`, ...), lalu **Test** untuk eksekusi langsung.
   - **Tanpa hardcode**: tidak ada IP / token / entity bawaan di source — semua URL dan
     token berasal dari input pengguna, dan daftar tombol mode HA memakai nama generik
     (`HA Key 1` … `HA Key 7`).
   - **Tanpa emoji**: seluruh ikon UI memakai sprite **Lucide** (set ikon yang sama
     dengan shadcn/ui) yang dirender sebagai SVG.
   - Endpoint backend: `GET /api/ha/status[?ping=1]`, `GET /api/ha/config`,
     `GET /api/ha/entities[?refresh=1]`, `POST /api/ha/test`,
     `POST /api/ha/config`, `POST /api/ha/call`.

> **Catatan**: endpoint `/api/*` hanya tersedia saat aplikasi dijalankan lewat
> [`linux-app/`](../linux-app/README.md) (native desktop app). Versi Docker murni hanya menyajikan
> file statis — pill HA akan menampilkan *Offline / Standalone* dan konfigurasi tombol tetap bisa disimpan
> sebagai profil JSON.

---

## 🐳 Cara Deploy di Homelab (Docker)

### 1. Menggunakan Docker Compose (Direkomendasikan)
Masuk ke direktori web-configurator:
```bash
cd /home/samvivan/Arduino/samvivanpad/macropadv2.5/web-configurator
docker compose up -d --build
```
Aplikasi sekarang berjalan di: **`http://<IP_HOMELAB_ANDA>:8080`**

### 2. Mengubah Port (Opsional)
Jika port `8080` sudah digunakan oleh aplikasi lain di homelab, jalankan dengan port custom:
```bash
PORT=9090 docker compose up -d
```

### 3. Menggunakan Docker CLI Biasa
```bash
docker build -t samvivan-macropad-studio:v2.5 .
docker run -d --name samvivan-macropad-studio -p 8080:80 --restart unless-stopped samvivan-macropad-studio:v2.5
```

---

## 🐧 Izin USB Serial di Linux Ubuntu (PENTING)

Agar browser (Chrome/Chromium/Brave) di Ubuntu memiliki izin membaca port Serial USB (`/dev/ttyUSB0` atau `/dev/ttyACM0`):

1. Masukkan user Anda ke dalam group `dialout`:
   ```bash
   sudo usermod -a -G dialout $USER
   ```
2. Pastikan izin akses port USB:
   ```bash
   sudo chmod a+rw /dev/ttyUSB0   # atau /dev/ttyACM0 jika terdeteksi ACM
   ```
3. Buka browser **Google Chrome** atau **Brave**, kunjungi URL homelab Anda (atau `http://localhost:8080`), lalu klik tombol **"Connect Device"**.
4. Pilih port ESP32 yang muncul pada pop-up browser.

---

## ⚡ Menjalankan Secara Lokal Tanpa Docker (Testing Cepat)
Anda dapat langsung menjalankan web server lokal menggunakan Node.js atau Python:

Menggunakan Python:
```bash
python3 -m http.server 8080
```
atau menggunakan `npx serve`:
```bash
npx -y serve -p 8080 .
```
Lalu buka `http://localhost:8080` di browser Anda.
