from preprocessing import preprocess_text
from bertopic_model import fit_bertopic
from utils import load_raw_data_to_list_comment
import argparse

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
    )

    # print("Identified Topics:", topics)
    topic_model.save(args.save_dir)
