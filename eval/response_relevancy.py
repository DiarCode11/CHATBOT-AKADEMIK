import pandas as pd
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import numpy as np

load_dotenv()

def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df

def embed_question(question: str, embedder: str = "text-embedding-3-small"):
    embeddings = OpenAIEmbeddings(model=embedder)
    vector_from_query = embeddings.embed_query(question)
    return vector_from_query

def cosine_similarity(vec1, vec2):
    # Hitung dot product
    dot_product = np.dot(vec1, vec2)
    
    # Hitung norma (magnitude) masing-masing vektor
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Hindari pembagian dengan nol
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    
    # Hitung cosine similarity
    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity

def calculate_relevancy(df: pd.DataFrame):
    data = {
        "PERTANYAAN ASLI": [],
        "PERTANYAAN BUATAN 1": [],
        "PERTANYAAN BUATAN 2": [],
        "PERTANYAAN BUATAN 3": [],
        "eg1": [],
        "eg2": [],
        "eg3": [],

    }

    for index, row in df.iterrows():
        embedding_question = embed_question(row['PERTANYAAN ASLI'])
        embedding1 = embed_question(row['PERTANYAAN BUATAN 1'])
        embedding2 = embed_question(row['PERTANYAAN BUATAN 2'])
        embedding3 = embed_question(row['PERTANYAAN BUATAN 3'])

        eg1 = cosine_similarity(embedding_question, embedding1)
        eg2 = cosine_similarity(embedding_question, embedding2)
        eg3 = cosine_similarity(embedding_question, embedding3)

        data["PERTANYAAN ASLI"].append(row['PERTANYAAN ASLI'])
        data["PERTANYAAN BUATAN 1"].append(row['PERTANYAAN BUATAN 1'])
        data["PERTANYAAN BUATAN 2"].append(row['PERTANYAAN BUATAN 2'])
        data["PERTANYAAN BUATAN 3"].append(row['PERTANYAAN BUATAN 3'])

        data["eg1"].append(eg1)
        data["eg2"].append(eg2)
        data["eg3"].append(eg3)

        print("\nIndex: ", index)
        print("Pertanyaan Asli: ", row['PERTANYAAN ASLI'])


    df = pd.DataFrame(data)
    df.to_csv("eval/dataset/response_relevancy_result.csv", index=False)
    print(df)


if __name__ == "__main__":
    df = read_csv("eval/dataset/Response Relevancy.csv")
    calculate_relevancy(df)

