from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

def create_vector_db():
    loader = PyPDFDirectoryLoader(path="data")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(documents)

    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

    vector_db = FAISS.from_documents(chunks, EMBEDDER)
    vector_db.save_local("src/db/akasha_db")


def get_pdf_list():
    pdf_list = os.listdir("data")

    frame = {
        "filename": [],
        "year": []
    }

    for pdf in pdf_list:
        if pdf.endswith(".pdf"):
            print("Data ditambahkan: ", pdf)
            frame["filename"].append(pdf)
            frame["year"].append(None)

    df = pd.DataFrame(frame)
    df.to_excel("dataset/pdf_list.xlsx", index=False, engine="openpyxl")

if __name__ == "__main__":
    get_pdf_list()