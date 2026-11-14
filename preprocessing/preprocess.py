import re
import unicodedata

try:
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
    factory = StopWordRemoverFactory()
    STOPWORDS = set(factory.get_stop_words())
except Exception:
    STOPWORDS = {
        "yang", "dan", "di", "ke", "dari", "ini", "itu",
        "untuk", "dengan", "pada", "adalah", "saya", "nya",
        "yg", "ga", "gak", "tidak"
    }


def preprocess_text(text):
    text = str(text).lower()
    text = unicodedata.normalize("NFKC", text)

    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#\w+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", " ", text)

    tokens = text.split()
    tokens = [word for word in tokens if word not in STOPWORDS]

    return " ".join(tokens)
