from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from src.state import AgentState
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

query = "siapa rektor undiksha"

vector_db_path = f"d:/SKRIPSI/CHATBOT AKADEMIK/src/db/db_20250222_220632"
db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
relevant_response = db.similarity_search_with_relevance_scores(query, k=5)

for index, doc in enumerate(relevant_response):
    print(f"Chunk ke {index}:")
    print(f"{doc}")