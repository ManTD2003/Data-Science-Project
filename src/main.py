from preprocessing import preprocess_text
from bertopic_model import fit_bertopic
from utils import load_raw_data_to_list_comment
import argparse
def int_or_str(value):
    try:
        return int(value)  # Try converting to int
    except ValueError:
        return str(value)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fit BERTopic model")
    parser.add_argument("--datapath", type=str, help="Input data file path", required=True)
    parser.add_argument(
        "--embedding_model_name",
        type=str,
        help="Embedding model name (default: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)",
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        help="Directory to save the BERTopic model (default: bertopic_model)",
        default="bertopic_model",
    )
    parser.add_argument(
        "--cache_dir",
        type=str,
        help="Cache directory for embeddings (default: None)",
        default=None,
    )
    parser.add_argument(
        "--nr_topic",
        type=int_or_str,
        help="Number of topics (default: 10, or a string keyword like 'auto')",
        default=10,
    )
    parser.add_argument(
        "--nr_range",
        type=tuple[int, int],
        help="Range of n-grams (default: (1, 3))",
        default=(1, 3),
    )
    args = parser.parse_args()

    docs = load_raw_data_to_list_comment(args.datapath)
    cleaned_docs = preprocess_text(docs)
    cleaned_docs = [doc for doc in cleaned_docs if doc.strip() != '']

    if not cleaned_docs:
        print("The list of documents after preprocessing is empty. Please check your data.")
        exit()

    topic_model, topics, probs = fit_bertopic(
        cleaned_docs,
        embedding_model_name=args.embedding_model_name,
        cache_dir=args.cache_dir,
        nr_topic=args.nr_topic,
        nr_range=args.nr_range,
    )

    topic_model.save(args.save_dir)
