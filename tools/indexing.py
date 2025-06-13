from langchain_community.document_loaders import PyPDFDirectoryLoader
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from app.utils.get_overlap import find_overlap
from dotenv import load_dotenv
from datetime import datetime
from app.models import Chunks
import pandas as pd
import numpy as np
import os
import uuid

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

def extract_text_from_pdf(filepath: str, year: str):
    """
    Extracts text from a PDF file and creates a Document object with metadata.

    Args:
        - filepath (str): The path to the PDF file to extract text from.
        - year (str): The year associated with the document for metadata.

    Returns:
        Document: A Document object containing the extracted text and metadata,
                  including the source filepath and year.
    """

    pdf = PdfReader(filepath)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    doc = Document(
            page_content=text, 
            metadata={
                "source": filepath,
                "year": year
            }
        )
    
    print("1. File berhasil di ekstrak")
    
    return doc

def load_documents(csv_path: str):
    """
    Loads documents from an Excel file and extracts their text content.

    Args:
        excel_path (str): The path to the Excel file containing document metadata,
                          including filenames and years.

    Returns:
        list: A list of Document objects, each containing the extracted text and 
              associated metadata from the PDF files specified in the Excel sheet.
    """

    df = pd.read_csv(csv_path)

    docs = []

    for index, row in df.iterrows():
        filename = row["file"]
        filepath = f"upload_docs/{filename}"
        extracted_text = extract_text_from_pdf(filepath=filepath, year=row["year"])
        docs.append(extracted_text)

    print("2. File berhasil dimuat")

    return docs

def get_pdf_list():
    pdf_list = os.listdir("data")

    frame = {
        "id": [],
        "file": [],
        "filetype": [],
        "year": [],
        "created_at": [],
        "updated_at": []
    }

    for pdf in pdf_list:
        if pdf.endswith(".pdf"):
            print("Data ditambahkan: ", pdf)
            unique_id = uuid.uuid4()
            frame["id"].append(str(unique_id))
            frame["file"].append(pdf)
            frame["filetype"].append("File Umum")
            frame["year"].append("2024")
            frame["created_at"].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            frame["updated_at"].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    df = pd.DataFrame(frame)
    df.to_csv("dataset/pdf_list.csv", index=False)

def create_db(csv_path: str, dest_path: str):
    """
    Creates a vector database from documents loaded from an Excel file.

    Args:
        csv_path (str): The path to the CSV file containing document metadata,
                          including filenames and years.
        dest_path (str): The path where the vector database will be saved.

    Returns:
        None

    Notes:
        The vector database is saved in the path specified by dest_path, and the
        filename is "akasha_db".

    """
    
    documents = load_documents(csv_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(documents)

    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

    vector_db = FAISS.from_documents(chunks, EMBEDDER)
    vector_db.save_local(dest_path)

    print("3. Database berhasil di buat")

def chunking(docs, size, overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    chunks = text_splitter.split_documents(docs)
    return chunks


def create_db_with_langchain(docs: list, chunk_size: int, chunk_overlap: int, embedding_model: str):    
    chunks = chunking(docs, chunk_size, chunk_overlap)
    print(chunks)

    for index, doc in enumerate(chunks):
        doc.metadata["index"] = index

    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=embedding_model)
    data = []
    try: 
        vector_db = FAISS.from_documents(chunks, EMBEDDER)
        faiss_index = vector_db.index
        total_vector = faiss_index.ntotal

        items_per_page = 5
        data = []

        for i in range(0, items_per_page):
            vector = faiss_index.reconstruct(i)
            doc = vector_db.docstore.search(vector_db.index_to_docstore_id[i])

            overlap = None
            
            if i > 0 and i < items_per_page - 1 :
                prev_doc = vector_db.docstore.search(vector_db.index_to_docstore_id[i-1])
                if doc.metadata["page"] == prev_doc.metadata["page"]:
                    overlap = find_overlap(prev_doc.page_content, doc.page_content)

            data.append(
                {
                    "index": i,
                    "vector": str(vector.tolist()),
                    "chunk": doc.page_content,
                    "metadata": doc.metadata,
                    "overlap": overlap
                }
            )


        if not os.path.exists("src/db"):
            os.makedirs("src/db")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        db_name = f"db_{timestamp}"

        vector_db.save_local(f"src/db/{db_name}")
        print()

        return {"status": "success", "message": f"Database {db_name} berhasil dibuat", "db_name": db_name, "data": data, "total_chunk": total_vector}
    
    except Exception as e:
        import traceback
        print("Error ketika membuat FAISS DB: ", str(e))
        print(traceback.format_exc()) 
        return {"status": "failed", "message": "Terjadi kesalahan saat membuat database"}


