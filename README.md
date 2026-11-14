# TikTok Sentiment Web

Aplikasi web untuk melakukan analisis sentimen ulasan produk TikTok Shop menggunakan metode **Support Vector Machine (SVM)** dengan ekstraksi fitur **Term Frequency–Inverse Document Frequency (TF-IDF)**.

Aplikasi ini dikembangkan menggunakan Python dan Flask untuk membantu proses pengolahan teks, klasifikasi sentimen, serta penyajian hasil analisis melalui antarmuka web.

## Fitur Utama

- Pengolahan teks (text preprocessing).
- Ekstraksi fitur menggunakan TF-IDF.
- Klasifikasi sentimen menggunakan Support Vector Machine (SVM).
- Integrasi model machine learning yang telah dilatih.
- Pengambilan ulasan produk menggunakan Apify.
- Antarmuka web menggunakan Flask, HTML, CSS, dan JavaScript.
- Penanganan kondisi ketika proses pengambilan ulasan mengalami kendala, termasuk security check.

## Teknologi yang Digunakan

| Teknologi             | Kegunaan                         |
| --------------------- | -------------------------------- |
| Python                | Bahasa pemrograman utama         |
| Flask                 | Web framework                    |
| Scikit-learn          | Machine learning                 |
| SVM                   | Algoritma klasifikasi            |
| TF-IDF                | Ekstraksi fitur teks             |
| Pandas                | Pengolahan data                  |
| Sastrawi              | Pemrosesan teks Bahasa Indonesia |
| Apify                 | Integrasi pengambilan data       |
| BeautifulSoup         | Parsing HTML                     |
| Playwright            | Browser automation               |
| HTML, CSS, JavaScript | Antarmuka aplikasi               |

## Struktur Project

```text
tiktok-sentiment-web/
│
├── app.py
├── apify_scraper.py
├── scraper.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── models/
│   ├── svm_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── README.txt
│
├── preprocessing/
│   ├── __init__.py
│   └── preprocess.py
│
├── scraper/
│   ├── __init__.py
│   └── tiktok_scraper.py
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/
    ├── base.html
    ├── index.html
    └── result.html
```

## Persyaratan

Pastikan perangkat telah memiliki:

- Python
- pip
- Git

## Instalasi dan Menjalankan Aplikasi

**1. Clone repository**

```bash
git clone https://github.com/Bambang-20/tiktok-sentiment-web.git
```

**2. Masuk ke direktori project**

```bash
cd tiktok-sentiment-web
```

**3. Buat virtual environment**

```bash
python -m venv .venv
```

**4. Aktifkan virtual environment**

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

**5. Instal dependensi**

```bash
pip install -r requirements.txt
```

**6. Konfigurasi API Apify (jika menggunakan fitur scraping)**

Buat file `.env` di direktori utama project:

```env
APIFY_API_TOKEN=masukkan_token_apify_kamu
```

Jangan membagikan file `.env` atau mengunggah API token ke repository publik.

**7. Jalankan aplikasi**

```bash
python app.py
```

**8. Buka aplikasi melalui browser**

```text
http://127.0.0.1:5000
```

## Model Machine Learning

Project ini menggunakan dua file model utama:

- `svm_model.pkl`: Model klasifikasi Support Vector Machine.
- `tfidf_vectorizer.pkl`: Model ekstraksi fitur TF-IDF.

Kedua file tersebut digunakan dalam proses klasifikasi teks ulasan produk.

## Catatan Penggunaan Scraper

Pengambilan data ulasan bergantung pada ketersediaan akses dari TikTok Shop dan layanan Apify.

Aplikasi tidak dirancang untuk melewati CAPTCHA atau mekanisme keamanan TikTok. Jika akses dibatasi atau ulasan tidak tersedia, sistem perlu menangani kondisi tersebut tanpa menghasilkan data yang keliru.

## Pengembangan Selanjutnya

- Penyempurnaan proses pengambilan data ulasan.
- Peningkatan pengujian dan evaluasi model klasifikasi.
- Penyempurnaan tampilan hasil analisis sentimen.
- Pengembangan statistik dan visualisasi hasil klasifikasi.
- Peningkatan dokumentasi dan pengujian aplikasi.

---

**Developer:** Triovand Susilo Timbang

**Project:** TikTok Sentiment Web

**Repository:** https://github.com/Bambang-20/tiktok-sentiment-web
