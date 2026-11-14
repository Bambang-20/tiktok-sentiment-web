"""
SCRAPER TIKTOK SHOP

Catatan:
- Modul ini tidak membypass CAPTCHA/security check.
- Jika TikTok Shop memberikan halaman security check atau tidak
  memberikan data review, fungsi mengembalikan daftar kosong.
- Endpoint internal dapat berubah sewaktu-waktu.
"""

import re
from urllib.parse import urlparse


def extract_product_id(url: str):
    match = re.search(r"/(\d{10,})", url)
    return match.group(1) if match else None


def scrape_reviews(url: str, max_reviews=100):
    """
    Placeholder aman untuk integrasi scraper.

    Return:
        {
            "product_id": "...",
            "product_name": "...",
            "reviews": [...]
        }

    Pada tahap integrasi nyata, fungsi ini akan dipanggil dari backend
    dan hasil review diproses oleh TF-IDF + SVM.
    """
    product_id = extract_product_id(url)

    return {
        "product_id": product_id,
        "product_name": "",
        "reviews": []
    }
