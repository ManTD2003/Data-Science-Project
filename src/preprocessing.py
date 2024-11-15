import re
from pyvi import ViTokenizer
from stop_words import get_stop_words


def load_vietnamese_stopwords():
    stopwords = set(get_stop_words("vietnamese"))
    return stopwords


def preprocess_text(docs: list[str]) -> list[str]:
    """
    Preprocess a list of documents.

    Args:
        docs (list[str]): List of documents.

    Returns:
        list[str]: List of preprocessed documents.
    """
    stop_words = load_vietnamese_stopwords()
    preprocessed_docs = []

    for doc in docs:
        doc = re.sub(r"[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯàáâãèéêìíòóôõùúăđĩũơư -]", " ", doc)
        doc = re.sub(r"\s+", " ", doc).strip()
        doc = ViTokenizer.tokenize(doc)
        words = doc.split()
        
        # remove stopwords
        # words = [word for word in words if word.lower() not in stop_words]
        
        preprocessed_doc = " ".join(words)
        preprocessed_docs.append(preprocessed_doc)

    return preprocessed_docs
