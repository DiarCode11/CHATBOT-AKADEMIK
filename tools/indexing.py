from langchain_community.document_loaders import PyPDFDirectoryLoader
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
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

def create_db_with_langchain():
    loader = PyPDFDirectoryLoader(path="upload_docs")
    documents = loader.load()

    df = pd.read_csv("dataset/pdf_list.csv")

    new_docs = []
    
    # Tambahkan metadata year
    for docs in documents:
        filepath = docs.metadata['source']
        filename = filepath.replace("upload_docs\\", "")
        row_selected = df.loc[df['file'] == filename]
        if not row_selected.empty:
            docs.metadata['year'] = row_selected['year'].values[0]
            new_docs.append(docs)
        else:
            docs.metadata['year'] = "2024"
            new_docs.append(docs)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(new_docs)

    print(len(chunks))
    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

    vector_db = FAISS.from_documents(chunks, EMBEDDER)

    if not os.path.exists("src/db"):
        os.makedirs("src/db")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    vector_db.save_local(f"src/db/db_{timestamp}")

if __name__ == "__main__":
    create_db(csv_path="dataset/pdf_list.csv", dest_path="src/db/akasha_db2")
