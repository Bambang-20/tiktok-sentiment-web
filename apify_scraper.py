import os
from dotenv import load_dotenv
from apify_client import ApifyClient


# ============================================================
# LOAD .ENV
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


# ============================================================
# APIFY TOKEN
# ============================================================

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

if not APIFY_TOKEN:
    raise RuntimeError(
        "APIFY_API_TOKEN belum ditemukan. "
        "Pastikan file .env berada di folder project "
        "dan berisi APIFY_API_TOKEN=..."
    )


# ============================================================
# APIFY CLIENT
# ============================================================

client = ApifyClient(APIFY_TOKEN)


# ============================================================
# ACTOR YANG DIPAKAI
# ============================================================

ACTOR_ID = "web_wanderer/tiktok-reviews-scraper"


# ============================================================
# CATATAN: BACKUP_DATASET_ID sudah DIHAPUS.
# Dulu ada fallback ke dataset hardcoded saat Actor gagal/kosong,
# tapi ini berbahaya: dataset itu isinya review dari produk lain,
# jadi hasilnya diam-diam salah tanpa disadari (review produk A
# ditampilkan seolah-olah untuk produk B). Sekarang kalau Actor
# gagal, fungsi return list kosong -- lalu app.py akan arahkan
# ke input manual, bukan data yang salah.
# ============================================================


def extract_review_rating(item):
    """
    Mengambil rating bintang (1-5) dari item hasil Apify.
    Mencoba beberapa nama field umum karena struktur bisa
    berbeda tergantung Actor.
    """

    if not isinstance(item, dict):
        return None

    possible_fields = [
        "rating",
        "review_rating",
        "star",
        "stars",
        "star_rating",
    ]

    for field in possible_fields:
        value = item.get(field)
        if value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                continue

    return None


# ============================================================
# EXTRACT REVIEW TEXT
# ============================================================

def extract_review_text(item):
    """
    Mengambil teks review dari item hasil Apify.
    Mencoba beberapa nama field umum karena struktur hasil
    Actor bisa berbeda-beda.
    """

    if not item:
        return None

    possible_fields = [
        "review",
        "reviewText",
        "review_text",
        "text",
        "comment",
        "content",
        "description",
        "message"
    ]

    for field in possible_fields:

        value = item.get(field)

        if value:

            value = str(value).strip()

            if value:
                return value

    return None


# ============================================================
# AMBIL DATASET APIFY
# ============================================================

def get_dataset_items(dataset_id, max_items=100):

    print()
    print("=" * 60)
    print("MENGAMBIL DATASET APIFY")
    print("=" * 60)
    print("Dataset ID:", dataset_id)

    try:
        dataset = client.dataset(dataset_id)
        items = []

        for item in dataset.iterate_items(clean=True):
            items.append(item)
            if len(items) >= max_items:
                break

        print("Jumlah item:", len(items))
        return items

    except Exception as e:
        print("DATASET ERROR:", e)
        return []


# ============================================================
# EXTRACT SEMUA REVIEW DARI DATASET
# ============================================================

def extract_reviews_from_items(items):

    reviews = []

    for item in items:
        review = extract_review_text(item)
        if review:
            reviews.append(review)

    return reviews


# (fungsi get_backup_reviews sudah dihapus - lihat catatan di atas)


# ============================================================
# AMBIL DATASET_ID DARI HASIL run ACTOR
# ============================================================

def _ambil_dataset_id(run):
    """
    Kompatibel dengan apify-client versi lama (run = dict)
    maupun versi baru 3.x (run = objek Run dengan atribut).
    """

    if run is None:
        return None

    if isinstance(run, dict):
        return run.get("defaultDatasetId")

    if hasattr(run, "default_dataset_id"):
        return run.default_dataset_id

    if hasattr(run, "defaultDatasetId"):
        return run.defaultDatasetId

    return None


# ============================================================
# SCRAPE TIKTOK REVIEWS
# ============================================================

def get_tiktok_reviews(product_id, max_reviews=1000):
    """
    PENTING: product_id WAJIB diisi oleh pemanggil (app.py).
    Tidak ada lagi fallback diam-diam ke produk default --
    kalau product_id kosong, fungsi ini berhenti dan melapor
    jelas, supaya tidak pernah salah kaprah menganalisis
    produk yang tidak diminta user.
    """

    if not product_id or not str(product_id).strip():
        print()
        print("=" * 60)
        print("PRODUCT_ID KOSONG")
        print("=" * 60)
        print("get_tiktok_reviews dipanggil tanpa product_id yang valid.")
        return []

    product_id = str(product_id).strip()

    print()
    print("=" * 60)
    print("MENJALANKAN ACTOR APIFY")
    print("=" * 60)
    print("Actor:", ACTOR_ID)
    print("Product ID:", product_id)
    print("Max reviews:", max_reviews)

    # --------------------------------------------------------
    # INPUT ACTOR
    # --------------------------------------------------------
    # PENTING: skema resmi Actor pakai "region" (default "US"
    # kalau tidak di-set!) dan "reviews_limit" (bukan hanya
    # "max_reviews"). Untuk produk Indonesia, region HARUS "ID"
    # -- ini kemungkinan besar penyebab "No reviews found" pada
    # produk yang sebenarnya punya banyak review.

    run_input = {
        "product_ids": [product_id],
        "region": "ID",
        "max_reviews": max_reviews,       # jaga-jaga kalau field lama masih dipakai
        "reviews_limit": max_reviews,     # nama field resmi
        "reviews_filter": "all",
        "reviews_sort": "recommended",
        "include_personal_information": False,
    }

    print()
    print("Input Actor:")
    print(run_input)

    # --------------------------------------------------------
    # RUN ACTOR
    # --------------------------------------------------------

    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)

    except Exception as e:
        print()
        print("=" * 60)
        print("ACTOR ERROR")
        print("=" * 60)
        print(e)

        # PENTING: TIDAK ada lagi fallback diam-diam ke dataset
        # backup. Dataset backup itu berisi review dari produk
        # LAIN (produk yang pernah ditest sebelumnya), jadi kalau
        # dipakai sebagai fallback, hasil analisis akan salah
        # tanpa disadari -- review produk A tapi dikira produk B.
        return []

    # --------------------------------------------------------
    # DATASET ID HASIL ACTOR (FIXED: kompatibel dict & objek Run)
    # --------------------------------------------------------

    dataset_id = _ambil_dataset_id(run)

    print()
    print("Dataset hasil Actor:", dataset_id)

    # --------------------------------------------------------
    # AMBIL DATASET
    # --------------------------------------------------------

    items = []

    if dataset_id:
        items = get_dataset_items(dataset_id, max_reviews)

    # --------------------------------------------------------
    # EXTRACT REVIEW (untuk cek jumlah & logging saja)
    # --------------------------------------------------------

    reviews_text = extract_reviews_from_items(items)

    # --------------------------------------------------------
    # JIKA ADA REVIEW
    # --------------------------------------------------------
    # PENTING: return ITEM MENTAH (dict), bukan cuma teksnya,
    # supaya field lain seperti rating tidak hilang sebelum
    # sampai ke app.py.

    if reviews_text:
        # Hanya sertakan item yang benar-benar punya teks review
        items_valid = [
            item for item in items
            if extract_review_text(item)
        ]

        print()
        print("=" * 60)
        print(f"SCRAPING BERHASIL: {len(items_valid)} REVIEW")
        print("=" * 60)
        return items_valid[:max_reviews]

    # --------------------------------------------------------
    # JIKA ACTOR TIDAK MENGHASILKAN REVIEW
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("TIDAK ADA REVIEW DARI SCRAPING")
    print("=" * 60)
    print("Product ID:", product_id)
    print("Actor berhasil jalan, tapi tidak menemukan review untuk produk ini.")

    # PENTING: TIDAK ada lagi fallback ke dataset backup.
    return []


if __name__ == "__main__":
    # Test terisolasi -- WAJIB isi product_id secara eksplisit,
    # tidak ada lagi default tersembunyi.
    test_product_id = "1733546667751212378"

    hasil = get_tiktok_reviews(test_product_id, max_reviews=20)

    print()
    print("HASIL AKHIR:", len(hasil), "review")
    for r in hasil[:5]:
        print("-", r)
