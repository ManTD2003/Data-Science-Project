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
    topics: List[int] = None,
    top_n_topics: int = None,
    use_ctfidf: bool = False,
    custom_labels: Union[bool, str] = False,
    umap_params: Dict[str, Any] = None,
    include_document_topics: bool = False,
    top_n_words: int = 10,
    docs: List[str] = None  # Thêm tham số docs nếu bạn muốn bao gồm tài liệu
) -> Dict[str, Any]:
    """
    Trích xuất toàn bộ thông tin các chủ đề từ mô hình BERTopic và trả về dưới dạng từ điển.

    Arguments:
        topic_model (BERTopic): Một thể hiện BERTopic đã được huấn luyện.
        topics (List[int], optional): Danh sách các chủ đề cần trích xuất. Nếu None, sẽ lấy tất cả các chủ đề hoặc theo top_n_topics.
        top_n_topics (int, optional): Chỉ chọn top n chủ đề phổ biến nhất. Nếu None, sẽ lấy tất cả các chủ đề hoặc theo danh sách topics.
        use_ctfidf (bool, optional): Sử dụng c-TF-IDF representations thay vì embeddings từ mô hình embedding.
        custom_labels (Union[bool, str], optional): 
            - Nếu là bool và True, sử dụng các nhãn tùy chỉnh đã được định nghĩa thông qua `topic_model.set_topic_labels`.
            - Nếu là str, sử dụng nhãn từ các khía cạnh khác, ví dụ: "Aspect1".
            - Nếu False, sử dụng nhãn mặc định.
        umap_params (Dict[str, Any], optional): Các tham số để cấu hình UMAP. Mặc định sẽ sử dụng các giá trị giống như BERTopic.
        include_document_topics (bool, optional): Nếu True, bao gồm danh sách các tài liệu thuộc về mỗi chủ đề.
        top_n_words (int, optional): Số lượng từ khóa hàng đầu cho mỗi chủ đề. Mặc định là 10.
        docs (List[str], optional): Danh sách các tài liệu gốc. Cần thiết nếu bạn muốn bao gồm `documents_per_topic`.

    Returns:
        Dict[str, Any]: Dữ liệu chứa thông tin các chủ đề và thông tin bổ sung.
    """

    if umap_params is None:
        umap_params = {
            "n_neighbors": 15,  # Thông thường BERTopic sử dụng 15
            "n_components": 2,
            "metric": "cosine",
            "random_state": 42
        }

    # 1. Lấy tần suất các chủ đề
    topic_freq = topic_model.get_topic_freq()
    topic_freq = topic_freq[topic_freq.Topic != -1]  # Loại bỏ chủ đề ngoại lai nếu có

    # 2. Chọn các chủ đề dựa trên tham số topics hoặc top_n_topics
    if topics is not None:
        selected_topics = list(topics)
    elif top_n_topics is not None:
        selected_topics = sorted(topic_freq.Topic.to_list()[:top_n_topics])
    else:
        selected_topics = sorted(topic_freq.Topic.to_list())

    # 3. Lấy các từ khóa của từng chủ đề với trọng số
    topics_words = {}
    for topic in selected_topics:
        topics_words[topic] = topic_model.get_topic(topic)[:top_n_words]  # Lấy top_n_words từ khóa

    # 4. Lấy kích thước (số lượng tài liệu) của từng chủ đề
    topic_sizes = topic_freq.set_index("Topic")["Count"].to_dict()

    # 5. Lấy nhãn tùy chỉnh nếu có
    if isinstance(custom_labels, str):
        # Giả sử rằng custom_labels là tên của một thuộc tính trong topic_model.topic_aspects_
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

    # 6. Lấy embedding của từng chủ đề
    if use_ctfidf and hasattr(topic_model, "c_tf_idf_"):
        embeddings = topic_model.c_tf_idf_
        c_tfidf_used = True
    else:
        embeddings = topic_model.topic_embeddings_
        c_tfidf_used = False

    # Chọn các embedding của các chủ đề được chọn
    all_topics = sorted(list(topic_model.get_topics().keys()))
    try:
        indices = np.array([all_topics.index(topic) for topic in selected_topics])
    except ValueError as e:
        print(f"Error finding topic index: {e}")
        return {}
    selected_embeddings = embeddings[indices]

    # 7. Tiền xử lý và giảm chiều bằng UMAP
    scaler = MinMaxScaler()
    scaled_embeddings = scaler.fit_transform(selected_embeddings)

    if c_tfidf_used:
        # BERTopic sử dụng metric "hellinger" khi sử dụng c-TF-IDF
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

    # 8. Tạo dữ liệu tổng hợp
    topics_data = []
    for i, topic in enumerate(selected_topics):
        topic_entry = {
            "topic_id": int(topic),
            "label": str(custom_labels_dict.get(topic, f"Topic {topic}")),
            "size": int(topic_sizes.get(topic, 0)),
            "words": [{"word": str(word), "weight": float(weight)} for word, weight in topics_words.get(topic, [])],
            "embedding": selected_embeddings[i].tolist(),
            "umap_x": float(umap_embeddings[i][0]),
            "umap_y": float(umap_embeddings[i][1]),
        }

        if include_document_topics and docs is not None:
            # Lấy danh sách các tài liệu thuộc về chủ đề này
            doc_info = topic_model.get_document_info(docs)
            documents = doc_info[doc_info.Topic == topic].Document.tolist()
            topic_entry["documents"] = documents

        topics_data.append(topic_entry)

    # 9. Thông tin bổ sung (tần suất các chủ đề)
    additional_info = {
        "topic_freq": topic_freq.to_dict(orient='records'),
        # "topic_similarities": topic_similarities.tolist(),  # Nếu bạn muốn thêm ma trận tương đồng
    }

    # 10. Tổng hợp tất cả dữ liệu
    all_data = {
        "topics": topics_data,
        "additional_info": additional_info,
    }

    return all_data