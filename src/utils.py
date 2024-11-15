import pandas as pd


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
