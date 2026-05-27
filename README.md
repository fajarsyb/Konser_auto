# Ticket Assistant (Operator Mode)

Ticket Assistant adalah aplikasi bantu untuk memantau halaman event konser, mendeteksi link/tombol tiket yang muncul secara publik, mengirim notifikasi Telegram, dan membuka link tiket secara otomatis untuk operator.

Aplikasi ini dirancang sebagai **operator-assist**, bukan bot auto-buy. Operator tetap melakukan klik final, CAPTCHA, login, pemilihan tiket, dan pembayaran secara manual.

## Fitur

- GUI sederhana berbasis Tkinter.
- Monitor banyak URL sekaligus.
- Deteksi link ke platform tiket seperti `tiket.com`, `loket.com`, `eventbrite.com`, dan lainnya.
- Deteksi tombol/link dengan kata kunci seperti `Beli`, `Buy`, `Pesan`, `Ticket`, `Checkout`.
- Kirim alert ke Telegram saat link/tombol tiket ditemukan.
- Auto-open link tiket pertama yang terdeteksi ke browser default.
- Log real-time di GUI.

## Batasan dan Etika Penggunaan

Program ini **tidak** melakukan:

- auto-submit pembelian,
- bypass CAPTCHA,
- bypass queue/waiting room,
- bypass anti-bot,
- scraping agresif,
- penyimpanan data kartu/CVV,
- manipulasi platform pihak ketiga.

Gunakan hanya untuk membaca halaman publik dengan interval wajar dan membantu operator manusia bertindak lebih cepat.

## Struktur File

```text
Automate/
├── main.py              # Entry point aplikasi
├── gui.py               # GUI Tkinter
├── engine.py            # Orkestrasi monitoring multi-URL
├── detector.py          # Scanner halaman publik
├── notifier.py          # Integrasi Telegram
├── requirements.txt     # Dependency Python
├── .env.example         # Template konfigurasi environment
└── README.md            # Dokumentasi
```

## Prasyarat

- Python 3.10+
- pip
- Browser engine Playwright Chromium
- Token Telegram Bot jika ingin memakai notifikasi Telegram

## Instalasi

### Windows
1. Pastikan Anda sudah menginstal Python (disarankan versi 3.10 ke atas) dan mencentang opsi **"Add Python to PATH"** saat instalasi.
2. Buka Command Prompt (CMD) atau PowerShell, lalu masuk ke folder project:
   ```cmd
   cd C:\path\to\Automate
   ```
3. Install dependency:
   ```cmd
   pip install -r requirements.txt
   ```
4. Install browser Chromium untuk Playwright:
   ```cmd
   playwright install chromium
   ```

### macOS
1. Pastikan Python 3 sudah terinstal (bisa lewat [python.org](https://www.python.org/) atau Homebrew `brew install python`).
2. Buka Terminal, masuk ke folder project:
   ```bash
   cd /path/to/Automate
   ```
3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Install browser Chromium untuk Playwright:
   ```bash
   playwright install chromium
   ```

### Linux (Ubuntu/Debian/Fedora)
1. Masuk ke folder project:
   ```bash
   cd /home/fajarsyb/code/Automate
   ```
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Install browser Chromium untuk Playwright:
   ```bash
   playwright install chromium
   ```

## Konfigurasi Telegram

Salin file `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Isi konfigurasi berikut:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=5
HEADLESS_MODE=False
USER_DATA_DIR=./user_sessions
```

### Cara Mendapatkan Telegram Bot Token

1. Buka Telegram.
2. Cari `@BotFather`.
3. Kirim `/newbot`.
4. Ikuti instruksi sampai mendapat token.
5. Masukkan token ke `TELEGRAM_BOT_TOKEN`.

### Cara Mendapatkan Chat ID

Cara paling mudah:

1. Kirim pesan ke bot yang baru dibuat.
2. Buka URL berikut di browser, ganti token dengan token bot kamu:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates
```

3. Cari field `chat.id`.
4. Masukkan nilainya ke `TELEGRAM_CHAT_ID`.

## Menjalankan Aplikasi

Jalankan:

```bash
python main.py
```

Akan muncul GUI dengan input daftar URL.

Contoh URL:

```text
https://fforeverindonesia.com/
https://www.loket.com/event/fforever30may
```

## Cara Pakai GUI

1. Masukkan daftar URL target, satu URL per baris.
2. Atur `Interval (detik)`.
   - Rekomendasi aman: `5` sampai `15` detik.
3. Atur `Maks cek`.
   - Contoh: `60` berarti scan maksimal 60 kali.
4. Centang `Auto-open link tiket saat terdeteksi` jika ingin browser otomatis membuka link tiket pertama.
5. Klik `Start Monitoring`.
6. Pantau log di bagian bawah GUI.
7. Jika link/tombol tiket terdeteksi:
   - log akan menampilkan hasil deteksi,
   - Telegram akan menerima notifikasi jika `.env` sudah benar,
   - link tiket akan dibuka otomatis jika opsi auto-open aktif.
8. Operator melanjutkan proses manual di browser.

## Contoh Alur War Tiket

1. T-30 menit: login manual ke platform terkait di browser utama.
2. T-10 menit: buka aplikasi Ticket Assistant.
3. Masukkan URL promotor atau URL event.
4. Set interval monitor, misalnya `5` detik.
5. Klik `Start Monitoring`.
6. Saat link/tombol tiket muncul, operator mendapat alert dan browser membuka link.
7. Operator menyelesaikan CAPTCHA, pemilihan tiket, dan pembayaran secara manual.

## Troubleshooting

### GUI tidak muncul (Tkinter Error)

Pastikan Python Tkinter sudah terpasang di sistem operasi Anda:

- **Windows:** Tkinter secara default sudah ikut terinstal saat Anda menginstal Python dari python.org. Jika hilang, jalankan ulang installer Python lalu pilih "Modify" dan pastikan opsi "tcl/tk and IDLE" dicentang.
- **macOS:** Jika Anda menggunakan Homebrew untuk menginstal Python, pastikan juga menginstal aspek tcl-tk:
  ```bash
  brew install python-tk
  ```
- **Fedora/RHEL/CentOS:**
  ```bash
  sudo dnf install python3-tkinter
  ```
- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install python3-tk
  ```

### Error Playwright browser belum tersedia

Jalankan:

```bash
playwright install chromium
```

### Telegram tidak terkirim

Cek hal berikut:

- `.env` sudah dibuat dari `.env.example`.
- `TELEGRAM_BOT_TOKEN` benar.
- `TELEGRAM_CHAT_ID` benar.
- Kamu sudah pernah mengirim pesan ke bot.
- Koneksi internet aktif.

### Deteksi tidak menemukan tombol

Kemungkinan:

- halaman membutuhkan login,
- tombol dibuat dinamis setelah interaksi tertentu,
- teks tombol berbeda dari keyword yang tersedia,
- tombol berada di iframe,
- platform memblokir akses headless/browser automation.

Solusi awal:

- tambahkan keyword baru di `BUY_KEYWORDS` pada `detector.py`,
- gunakan URL promotor yang lebih langsung,
- turunkan interval dengan wajar,
- cek apakah link tiket tersedia sebagai `<a href="...">` publik.

## Catatan Pengembangan Berikutnya

Fitur yang bisa ditambahkan nanti:

- penyimpanan daftar URL ke SQLite,
- profil event dengan waktu on-sale,
- countdown T-0 di GUI,
- suara alarm saat temuan terdeteksi,
- mode dry-run untuk simulasi,
- export log ke file CSV/JSON,
- Telegram command `/status` dan `/stop`.

## Keamanan

- Jangan commit file `.env`.
- Jangan simpan password, OTP, CVV, atau kartu pembayaran di aplikasi.
- Jangan menaruh token Telegram langsung di source code.
- Gunakan interval monitoring yang wajar agar tidak membebani website target.
# Konser_auto
