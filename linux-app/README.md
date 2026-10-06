# 🎛️ SamVivan MacroPad - Native Linux Desktop Application

Aplikasi desktop native untuk Linux Ubuntu (seperti **Razer Synapse, Logitech G Hub, Vial, Piper, atau OpenRGB**).

Aplikasi ini **bukan daemon yang terus berjalan di background**, melainkan aplikasi desktop mandiri:
* Muncul di **Menu Aplikasi Ubuntu** (Dash / App Launcher).
* Membuka jendela aplikasi native GTK3 dengan akselerasi hardware.
* Memindai aplikasi terpasang di sistem Ubuntu secara otomatis (142 aplikasi).
* Memungkinkan konfigurasi tombol, aksi shortcut, peluncur aplikasi, dan otomasi audio.
* Saat jendela ditutup, seluruh proses aplikasi berhenti dengan bersih.

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
- Modul: [`home_assistant.py`](home_assistant.py) (`HomeAssistantClient`).
- Endpoint lokal:
  - `GET /api/ha/status` — instan dari cache; `?ping=1` untuk cek live (timeout 1 dtk).
  - `GET /api/ha/config`, `POST /api/ha/config` — simpan/baca URL + token.
  - `GET /api/ha/entities[?refresh=1]` — daftar entity (cache / scan ulang).
  - `POST /api/ha/test` — uji koneksi dengan URL + token yang belum disimpan.
  - `POST /api/ha/call` — panggil service HA (`domain`, `service`, `entity_id`).
- Ikon domain memakai set ikon **Lucide** (sama dengan shadcn/ui), termasuk pemetaan
  `mdi:*` dari atribut icon Home Assistant.
- Setiap eksekusi aksi HA mengirim notifikasi desktop via `notify-send`.
- Jika HA tidak terjangkau, daftar entity jatuh ke cache terakhir di disk; scan ulang
  otomatis ditahan 30 detik supaya endpoint tetap instan.

---

## 🗑️ Cara Uninstall

Untuk menghapus aplikasi dari menu aplikasi Ubuntu dan membersihkan shortcut serta ikon:

```bash
cd /home/samvivan/Arduino/samvivanpad/macropadv2.5/linux-app
./uninstall.sh
```
