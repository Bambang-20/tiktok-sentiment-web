import re
import requests
from bs4 import BeautifulSoup


# ============================================================
# EKSTRAK PRODUCT ID
# ============================================================

def extract_product_id(url):

    pattern = r"/(\d{10,})(?:\?|$)"

    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


# ============================================================
# CEK HALAMAN PRODUK
# ============================================================

def check_product_page(url):

    print("=" * 60)
    print("MEMERIKSA HALAMAN PRODUK")
    print("=" * 60)

    print("URL:")
    print(url)

    product_id = extract_product_id(url)

    if product_id:

        print()
        print("✓ Product ID ditemukan:")
        print(product_id)

    else:

        print()
        print("❌ Product ID tidak ditemukan")

        return None

    headers = {

        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36",

        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

        "Accept-Language":
        "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"

    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print()
        print("HTTP Status:", response.status_code)

        print(
            "Ukuran response:",
            len(response.text),
            "bytes"
        )

        # ----------------------------------------------------
        # SECURITY CHECK
        # ----------------------------------------------------

        text_lower = response.text.lower()

        security_words = [

            "security check",
            "captcha",
            "verify you are human",
            "verification",
            "challenge"

        ]

        detected = None

        for word in security_words:

            if word in text_lower:

                detected = word

                break

        if detected:

            print()
            print("⚠ SECURITY CHECK TERDETEKSI")
            print("Tanda:", detected)

            print()
            print(
                "Halaman tidak memberikan review "
                "kepada scraper."
            )

            print(
                "Tidak mencoba melewati security."
            )

            return {

                "success": False,

                "product_id": product_id,

                "reviews": [],

                "reason": "security_check"

            }

        # ----------------------------------------------------
        # PARSE HTML
        # ----------------------------------------------------

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = soup.title.text.strip() if soup.title else ""

        print()
        print("TITLE:")
        print(title)

        return {

            "success": True,

            "product_id": product_id,

            "reviews": [],

            "reason": "review_not_found"

        }

    except Exception as e:

        print()
        print("❌ ERROR:")
        print(str(e))

        return {

            "success": False,

            "product_id": product_id,

            "reviews": [],

            "reason": "request_error",

            "error": str(e)

        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    url = input(
        "Masukkan link produk TikTok Shop: "
    ).strip()

    result = check_product_page(url)

    print()
    print("=" * 60)
    print("HASIL")
    print("=" * 60)

    if result:

        print(
            "Product ID:",
            result["product_id"]
        )

        print(
            "Status:",
            result["reason"]
        )

        print(
            "Jumlah review:",
            len(result["reviews"])
        )

    else:

        print("❌ URL tidak valid")