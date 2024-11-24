import re
import os
import pdfplumber
import pandas as pd
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()


# load env
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

# def extract_text_from_pdf(path: str):
#     # Variabel untuk menyimpan teks gabungan
#     full_text = ""

#     # Membaca teks dari semua halaman
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             # Tambahkan teks dari setiap halaman ke variabel full_text
#             full_text += page.extract_text() + " "

#     # Menghapus teks yang cocok dengan regex
#     cleaned_text = re.sub(r"Pedoman Studi Universitas Pendidikan Ganesha Tahun 2017 \d{1,3}", "", full_text)

#     # Menambahkan "\n\n" sebelum nama program studi
#     updated_text = re.sub(r'(\d+\.\sProgram Studi.*?)', r'\n\n\1', cleaned_text)

#     # Hasil: Teks gabungan dari semua halaman
#     print(updated_text)
#     return updated_text


# def create_docs(path: str, desc: str):
#     # Ekstraksi teks dari file PDF
#     text = extract_text_from_pdf(path)

#     # Membuat objek Document
#     docs = [Document(page_content=text, metadata={"description": desc, "file_path": path})]
#     print(docs)
#     return docs

# def load_and_split_pdf(path: str):
#     docs = create_docs(path, "Pedoman Studi Universitas Pendidikan Ganesha Tahun 2017")
#     print("STEP 1: Document has been loaded successfully\n")

#     text_splitter = RecursiveCharacterTextSplitter(
#         separators=["\n\n\n"],
#         chunk_size=2000,
#         chunk_overlap=500
#     )

#     splitted_docs = text_splitter.split_documents(docs)
#     print("STEP 2: Document has been splitted successfully\n")
#     return splitted_docs

def combine_excel_file():
    path = "data_excel"
    # List semua file dalam folder
    excel_files = os.listdir(path)

    # Gabungkan semua file
    dataframes = []
    for file in excel_files:
        file_path = os.path.join(path, file)
        df = pd.read_excel(file_path)
        dataframes.append(df)

    # Gabungkan semua DataFrame menjadi satu
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Simpan hasil ke file Excel baru (opsional)
    combined_df.to_excel("combined_data/combined.xlsx", index=False)

def create_docs(path: str):
    df = pd.read_excel(path)

    frame = []
    
    for index, row in df.iterrows():
        docs = Document(page_content=row["content"], metadata={"description": row["description"], "file_path": row["file_path"], "year": row["year"]})
        frame.append(docs)
    
    return frame

def create_vector_db():
    # Load dokumen PDF
    chunks = create_docs(path="combined_data/combined.xlsx")

    # Split dokumen PDF
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Cek apakah ada vectorstore belum ada
    if not os.path.exists("vector_db"):
        # Buat vectorstore
        vectorstore = FAISS.from_documents(chunks, embeddings)

        # Simpan vectorstore ke disk (opsional tapi direkomendasikan)
        vectorstore.save_local("vector_db")
        print("STEP 3: Vectorstore has been created")

    else:
        print("""WARNING: The vector database already exists, please check the "vector_db" folder""")
    
def delete_vector_db():
    if os.path.exists("vector_db"):
        os.remove("vector_db")
        print("Vectorstore has been deleted")
    else:
        print("""WARNING: The vector database doesn't exist, please check the "vector_db" folder""")


if __name__ == "__main__":
    create_vector_db()
    