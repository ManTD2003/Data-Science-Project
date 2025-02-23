from bertopic import BERTopic  # Cập nhật import
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from underthesea import word_tokenize
from stop_words import get_stop_words
from bertopic.representation import MaximalMarginalRelevance

def vietnamese_tokenizer(text):
    return word_tokenize(text)

def fit_bertopic(
    docs: list[str],
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    cache_dir: str | None = None,
    nr_topic: str | int = 10,
    nr_range: tuple[int, int] = (1, 3),
):
    """
    Fit BERTopic model on the given data and return the model, topics, and probabilities.

    Args:
        docs (list[str]): List of documents.
        embedding_model_name (str, optional): Embedding model name. Defaults to a multilingual model.
        cache_dir (str, optional): Cache directory. Defaults to None.

    Returns:
        BERTopic: Trained BERTopic model.
        list[int]: Topics.
        list[float]: Probabilities.
    """

    embedding_model = SentenceTransformer(embedding_model_name, cache_folder=cache_dir, device='cuda')

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')

    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean',
                            cluster_selection_method='eom', prediction_data=True)

    vietnamese_stopwords = get_stop_words('vietnamese')

    vectorizer_model = CountVectorizer(
        tokenizer=vietnamese_tokenizer,
        stop_words=vietnamese_stopwords,
        ngram_range=nr_range,
        token_pattern=None,
        lowercase=False,
        strip_accents=None
    )

    ctfidf_model = ClassTfidfTransformer()

    representation_model = MaximalMarginalRelevance(diversity=0.7)

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        ctfidf_model=ctfidf_model,
        representation_model=representation_model,
        nr_topics=nr_topic
    )

    topics, probs = topic_model.fit_transform(docs)

    return topic_model, topics, probs

def load_bert_model(model_path: str):
    """
    Load BERTopic model from the given path.

    Args:
        model_path (str): Path to the saved model.

    Returns:
        BERTopic: Loaded BERTopic model.
    """
    return BERTopic.load(model_path)
