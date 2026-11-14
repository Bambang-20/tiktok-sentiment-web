from flask import Flask, render_template, request
import os
import re
import joblib

import re
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from apify_scraper import get_tiktok_reviews, extract_review_text, extract_review_rating

app = Flask(__name__)


# ============================================================
# SASTRAWI: STOPWORD & STEMMER
# (WAJIB SAMA dengan yang dipakai di notebook training,
#  supaya tidak ada train-serving skew)
# ============================================================

_factory_stopword = StopWordRemoverFactory()
_stopwords = set(_factory_stopword.get_stop_words())

_factory_stemmer = StemmerFactory()
_stemmer = _factory_stemmer.create_stemmer()

print("=" * 60)
print("SASTRAWI STOPWORD & STEMMER SIAP")
print("Jumlah stopword:", len(_stopwords))
print("=" * 60)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# LOAD MODEL TF-IDF & SVM
# ============================================================

TFIDF_PATH = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")
SVM_PATH = os.path.join(BASE_DIR, "models", "svm_model.pkl")

try:
    tfidf = joblib.load(TFIDF_PATH)
    svm = joblib.load(SVM_PATH)

    print("=" * 60)
    print("MODEL TF-IDF DAN SVM BERHASIL DIMUAT")
    print("=" * 60)

except Exception as e:
    print("=" * 60)
    print("GAGAL MEMUAT MODEL")
    print("=" * 60)
    print("Error:", e)
    raise


# ============================================================
# PREPROCESSING
# ============================================================

def preprocess_text(text):
    """
    HARUS SAMA PERSIS dengan preprocessing di notebook training
    (Cell "PREPROCESSING TEXT"), supaya tidak ada train-serving
    skew -- yaitu model menerima bentuk teks yang beda dari yang
    dia pelajari saat training, yang bisa menurunkan akurasi
    prediksi secara signifikan.
    """

    text = str(text)

    # Lowercase
    text = text.lower()

    # Hapus URL
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    # Hapus email
    text = re.sub(r'\S+@\S+', ' ', text)

    # Hapus mention
    text = re.sub(r'@\w+', ' ', text)

    # Hapus hashtag tapi pertahankan katanya
    text = re.sub(r'#(\w+)', r'\1', text)

    # Hapus angka
    text = re.sub(r'\d+', ' ', text)

    # Hapus tanda baca
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Hapus karakter non-huruf
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenisasi sederhana
    tokens = text.split()

    # Stopword removal
    tokens = [word for word in tokens if word not in _stopwords]

    text = ' '.join(tokens)

    # Stemming
    if text:
        text = _stemmer.stem(text)

    return text.strip()


# ============================================================
# NORMALISASI SENTIMEN
# ============================================================

def normalize_sentiment(sentiment):
    """
    Encoding model: 0 = negatif, 1 = netral, 2 = positif
    """

    if sentiment is None:
        return "netral"

    value = str(sentiment).strip().lower()

    if value == "0":
        return "negatif"
    if value == "1":
        return "netral"
    if value == "2":
        return "positif"

    if value in ["positive", "positif", "pos"]:
        return "positif"
    if value in ["negative", "negatif", "neg"]:
        return "negatif"
    if value in ["neutral", "netral", "neu"]:
        return "netral"

    if "posit" in value:
        return "positif"
    if "negat" in value:
        return "negatif"
    if "netral" in value or "neutral" in value:
        return "netral"

    print(f"⚠️ Label sentimen tidak dikenali: {value!r}")
    return "netral"


# ============================================================
# PREDIKSI SENTIMEN
# ============================================================

def predict_sentiment(review):
    cleaned = preprocess_text(review)

    if not cleaned:
        return "netral"

    vector = tfidf.transform([cleaned])
    prediction = svm.predict(vector)[0]

    return normalize_sentiment(prediction)


# ============================================================
# ANALISIS REVIEW
# ============================================================

def rating_to_sentiment(rating):
    """
    Aturan SAMA PERSIS seperti Cell 8 di notebook training:
        rating <= 3  -> negatif
        rating == 4  -> netral
        rating >= 5  -> positif

    Dipakai untuk membandingkan "sentimen versi rating" dengan
    "sentimen versi prediksi model SVM" -- membantu mendeteksi
    kasus mismatch (mis. rating 5 tapi model bilang negatif).
    """
    if rating is None:
        return None

    if rating <= 3:
        return "negatif"
    elif rating == 4:
        return "netral"
    else:
        return "positif"


def analyze_reviews(reviews):
    results = []

    for review in reviews:

        if isinstance(review, dict):
            review_text = extract_review_text(review)
            rating = extract_review_rating(review)
        else:
            review_text = str(review).strip()
            rating = None

        if not review_text:
            continue

        sentiment = predict_sentiment(review_text)
        rating_sentiment = rating_to_sentiment(rating)

        # Mismatch: model (dari teks) vs rating -- keduanya ada,
        # tapi hasilnya beda. Ini bagus untuk analisis kesalahan
        # di skripsi (Bab 4/5).
        is_mismatch = (
            rating_sentiment is not None
            and sentiment != rating_sentiment
        )

        results.append({
            "review": review_text,
            "review_text": review_text,  # alias, biar cocok dgn template result.html
            "sentiment": sentiment,           # hasil prediksi model SVM (dari teks)
            "rating": rating,                 # rating asli (1-5) dari Apify
            "rating_sentiment": rating_sentiment,  # sentimen versi aturan rating
            "is_mismatch": is_mismatch,       # True kalau model & rating tidak sejalan
        })

    return results


# ============================================================
# HITUNG STATISTIK
# ============================================================

def calculate_stats(results):
    positif = 0
    negatif = 0
    netral = 0
    mismatch = 0

    for item in results:
        sentiment = normalize_sentiment(item.get("sentiment"))

        if sentiment == "positif":
            positif += 1
        elif sentiment == "negatif":
            negatif += 1
        else:
            netral += 1

        if item.get("is_mismatch"):
            mismatch += 1

    total = positif + negatif + netral

    return {
        "positif": positif,
        "negatif": negatif,
        "netral": netral,
        "total": total,
        "mismatch": mismatch,
    }


# ============================================================
# EXTRACT PRODUCT ID DARI URL / INPUT ID LANGSUNG
# ============================================================

def extract_product_id(url):
    if not url:
        return None

    match = re.search(r"/pdp/[^/]+/(\d{10,})", url)
    if match:
        return match.group(1)

    match = re.search(r"/pdp/(\d{10,})", url)
    if match:
        return match.group(1)

    match = re.search(r"(\d{10,})", url)
    if match:
        return match.group(1)

    return None


# ============================================================
# HOME (SATU-SATUNYA ROUTE)
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():

    results = []
    error = None
    product_id = None
    product_url = ""
    total_reviews = 0
    source = None

    stats = {"positif": 0, "negatif": 0, "netral": 0, "total": 0}

    if request.method == "POST":

        product_url = request.form.get("url", "").strip()

        if not product_url:
            error = "URL atau ID produk harus diisi."

        else:
            product_id = extract_product_id(product_url)

            if not product_id:
                error = "Product ID tidak ditemukan dari input."

            else:
                print()
                print("=" * 60)
                print("ANALISIS SENTIMEN TIKTOK SHOP")
                print("=" * 60)
                print("Input:", product_url)
                print("Product ID:", product_id)
                print("=" * 60)

                try:
                    print()
                    print("Mengambil review berdasarkan Product ID...")

                    reviews = get_tiktok_reviews(
                        product_id=product_id,
                        max_reviews=100,
                    )

                    if reviews:
                        source = "Apify"
                        total_reviews = len(reviews)

                        print()
                        print("✓ REVIEW BERHASIL DIAMBIL")
                        print("Jumlah:", total_reviews)

                        results = analyze_reviews(reviews)
                        stats = calculate_stats(results)

                        print()
                        print("=" * 60)
                        print("HASIL ANALISIS")
                        print("=" * 60)
                        print("Positif:", stats["positif"])
                        print("Negatif:", stats["negatif"])
                        print("Netral:", stats["netral"])
                        print("Total:", stats["total"])
                        print("=" * 60)

                    else:
                        error = f"Tidak ditemukan review untuk Product ID {product_id}."
                        print()
                        print("⚠ Tidak ada review.")

                except Exception as e:
                    print()
                    print("=" * 60)
                    print("APIFY ERROR")
                    print("=" * 60)
                    print(repr(e))
                    print("=" * 60)

                    error = (
                        "Terjadi kesalahan saat mengambil review dari Apify. "
                        "Periksa terminal untuk detail error."
                    )

    return render_template(
        "index.html",
        results=results,
        error=error,
        product_id=product_id,
        product_url=product_url,
        total_reviews=total_reviews,
        source=source,
        stats=stats,
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    import webbrowser
    import threading

    threading.Timer(
        1.5,
        lambda: webbrowser.open("http://127.0.0.1:5000")
    ).start()

    app.run(debug=True, use_reloader=False)