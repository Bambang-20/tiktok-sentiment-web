# TikTok Sentiment Web

Aplikasi web untuk analisis sentimen ulasan produk TikTok Shop
menggunakan preprocessing, TF-IDF, dan Support Vector Machine (SVM).

## Struktur

- `app.py` = backend Flask
- `models/` = model TF-IDF dan SVM
- `scraper/` = modul scraper
- `preprocessing/` = preprocessing teks
- `templates/` = halaman web
- `static/` = CSS dan JavaScript
- `database/` = SQLite

## Menjalankan

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Jalankan:

```bash
python app.py
```

Buka:

http://127.0.0.1:5000

## Tahap berikutnya

1. Masukkan model TF-IDF hasil training.
2. Masukkan model SVM hasil training.
3. Hubungkan preprocessing.
4. Hubungkan scraper TikTok Shop.
5. Simpan review ke database.
6. Jalankan klasifikasi SVM.
7. Tampilkan statistik sentimen di web.

Catatan: scraper tidak membypass CAPTCHA/security check.
Jika TikTok Shop tidak memberikan review ke sesi/browser,
sistem harus menangani kondisi tersebut secara aman.
