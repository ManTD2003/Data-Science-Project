import pandas as pd
import json
from typing import List, Union, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import umap
from bertopic import BERTopic

def save_texts_to_file(texts: list[str], file_path: str):
    """
    Save texts to a file, each text on a new line.

    Args:
        texts (list[str]): List of texts.
        file_path (str): Path to the output file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text + '\n')


def load_raw_data_to_list_comment(file_path: str) -> list[str]:
    """
    Load the 'content' column from a CSV file into a list, excluding empty or None comments.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list[str]: List of non-empty comments from the 'content' column.
    """
    df = pd.read_csv(file_path, encoding='utf-8')
    df = df.dropna(subset=['content'])
    comments = df['content'].astype(str)
    comments = comments[comments.str.strip() != '']
    return comments.tolist()

def extract_all_topics_data(
    topic_model: BERTopic,
    output_file: str = "all_topics_data.json",
    topics: List[int] = None,
    top_n_topics: int = None,
    use_ctfidf: bool = False,
    custom_labels: Union[bool, str] = False,
    umap_params: Dict[str, Any] = None,
    include_document_topics: bool = False,
    top_n_words: int = 10
):

    if umap_params is None:
        umap_params = {
            "n_neighbors": 15,  
            "n_components": 2,
            "metric": "cosine",
            "random_state": 42
        }

    topic_freq = topic_model.get_topic_freq()
    topic_freq = topic_freq[topic_freq.Topic != -1]  

    if topics is not None:
        selected_topics = list(topics)
    elif top_n_topics is not None:
        selected_topics = sorted(topic_freq.Topic.to_list()[:top_n_topics])
    else:
        selected_topics = sorted(topic_freq.Topic.to_list())

    topics_words = {}
    for topic in selected_topics:
        topics_words[topic] = topic_model.get_topic(topic)[:top_n_words]  

    topic_sizes = topic_freq.set_index("Topic")["Count"].to_dict()

    if isinstance(custom_labels, str):
        if hasattr(topic_model, "topic_aspects_") and custom_labels in topic_model.topic_aspects_:
            words = [
                "_".join([label[0] for label in topic_model.topic_aspects_[custom_labels][topic][:4]])
                for topic in selected_topics
            ]
            custom_labels_dict = {topic: (label if len(label) < 30 else label[:27] + "...") 
                                  for topic, label in zip(selected_topics, words)}
        else:
            custom_labels_dict = {topic: f"Topic {topic}" for topic in selected_topics}
    elif custom_labels and hasattr(topic_model, "custom_labels_") and topic_model.custom_labels_ is not None:
        custom_labels_dict = {topic: label for topic, label in topic_model.custom_labels_.items() if topic in selected_topics}
    else:
        custom_labels_dict = {topic: f"Topic {topic}" for topic in selected_topics}

    if use_ctfidf and hasattr(topic_model, "c_tf_idf_"):
        embeddings = topic_model.c_tf_idf_
        c_tfidf_used = True
    else:
        embeddings = topic_model.topic_embeddings_
        c_tfidf_used = False

    all_topics = sorted(list(topic_model.get_topics().keys()))
    indices = np.array([all_topics.index(topic) for topic in selected_topics])
    selected_embeddings = embeddings[indices]

    scaler = MinMaxScaler()
    scaled_embeddings = scaler.fit_transform(selected_embeddings)

    if c_tfidf_used:
        umap_model = umap.UMAP(
            n_neighbors=umap_params.get("n_neighbors", 15),
            n_components=umap_params.get("n_components", 2),
            metric=umap_params.get("metric", "hellinger"),
            random_state=umap_params.get("random_state", 42)
        )
    else:
        umap_model = umap.UMAP(
            n_neighbors=umap_params.get("n_neighbors", 15),
            n_components=umap_params.get("n_components", 2),
            metric=umap_params.get("metric", "cosine"),
            random_state=umap_params.get("random_state", 42)
        )

    umap_embeddings = umap_model.fit_transform(scaled_embeddings)

    topics_data = []
    for i, topic in enumerate(selected_topics):
        topic_entry = {
            "topic_id": topic,
            "label": custom_labels_dict.get(topic, f"Topic {topic}"),
            "size": topic_sizes.get(topic, 0),
            "words": [{"word": word, "weight": weight} for word, weight in topics_words.get(topic, [])],
            "embedding": selected_embeddings[i].tolist(),
            "umap_x": umap_embeddings[i][0],
            "umap_y": umap_embeddings[i][1],
        }

        if include_document_topics:
            pass  

        topics_data.append(topic_entry)

    additional_info = {
        "topic_freq": topic_freq.to_dict(orient='records'),
        # "topic_similarities": topic_similarities.tolist(),
    }

    all_data = {
        "topics": topics_data,
        "additional_info": additional_info,
    }
    
    return all_data