from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

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
vector_db.save_local("src/agents/akasha_db")