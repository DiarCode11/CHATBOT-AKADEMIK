from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os

load_dotenv()

def load_and_split_pdf(path: str):
    loader = PyPDFLoader(path)
    pages = loader.load()
    print("STEP 1: Document has been loaded successfully\n")

    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200
    )

    docs = text_splitter.split_documents(pages)
    print("STEP 2: Document has been splitted successfully\n")
    return docs

def create_vector_db():
    # Load dokumen PDF
    splits_docs = load_and_split_pdf(path="data/Pedoman-Studi-2017.pdf")

    # Split dokumen PDF
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Cek apakah ada vectorstore belum ada
    if not os.path.exists("vector_db"):
        # Buat vectorstore
        vectorstore = FAISS.from_documents(splits_docs, embeddings)

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

create_vector_db()



    