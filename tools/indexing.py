from langchain_community.document_loaders import PyPDFDirectoryLoader
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pandas as pd
import os

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

def load_documents(excel_path: str):
    """
    Loads documents from an Excel file and extracts their text content.

    Args:
        excel_path (str): The path to the Excel file containing document metadata,
                          including filenames and years.

    Returns:
        list: A list of Document objects, each containing the extracted text and 
              associated metadata from the PDF files specified in the Excel sheet.
    """

    df = pd.read_excel(excel_path, engine="openpyxl")

    docs = []

    for index, row in df.iterrows():
        filename = row["filename"]
        filepath = f"data/{filename}"
        extracted_text = extract_text_from_pdf(filepath=filepath, year=row["year"])
        docs.append(extracted_text)

    print("2. File berhasil dimuat")

    return docs

def create_db(excel_path: str, dest_path: str):
    """
    Creates a vector database from documents loaded from an Excel file.

    Args:
        excel_path (str): The path to the Excel file containing document metadata,
                          including filenames and years.
        dest_path (str): The path where the vector database will be saved.

    Returns:
        None

    Notes:
        The vector database is saved in the path specified by dest_path, and the
        filename is "akasha_db".

    """
    
    documents = load_documents(excel_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(documents)

    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

    vector_db = FAISS.from_documents(chunks, EMBEDDER)
    vector_db.save_local(dest_path)

    print("3. Database berhasil di buat")

def create_db_with_langchain():
    loader = PyPDFDirectoryLoader(path="data")
    documents = loader.load()
    print(documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(documents)

    print(len(chunks))
    EMBEDDER = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

    vector_db = FAISS.from_documents(chunks, EMBEDDER)
    vector_db.save_local("src/db/akasha_db")

if __name__ == "__main__":
    create_db_with_langchain()