from datetime import datetime
import os
import pandas as pd
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

def load_documents(path):
    loader = PyPDFDirectoryLoader(path=path)
    return loader.load()

def load_dataframe(csv_path):
    return pd.read_csv(csv_path)

def process_documents(documents, df):
    new_docs = []
    for docs in documents:
        filepath = docs.metadata['source']
        filename = filepath.replace("upload_docs\\", "")
        row_selected = df.loc[df['file'] == filename]
        if not row_selected.empty:
            docs.metadata['year'] = row_selected['year'].values[0]
        else:
            docs.metadata['year'] = "2024"
        new_docs.append(docs)
    return new_docs

def split_documents(documents, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n"]
    )
    return text_splitter.split_documents(documents)

def create_db_with_langchain(chunk_size=1000, chunk_overlap=400):
    # Memuat dokumen dan DataFrame 
    documents = load_documents("upload_docs")
    df = load_dataframe("dataset/pdf_list.csv")
    
    # Memproses dokumen untuk menambahkan metadata 'year'
    new_docs = process_documents(documents, df)
    
    # Membagi dokumen menjadi potongan-potongan teks
    chunks = split_documents(new_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(len(chunks))
    
    # Inisialisasi embedder
    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
    
    # Membuat basis data vektor
    vector_db = FAISS.from_documents(chunks, EMBEDDER)
    
    # Menyimpan basis data vektor
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory_name = f"src/db/db_{timestamp}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    vector_db.save_local(directory_name)


