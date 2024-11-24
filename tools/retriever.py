from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# Load embedding model
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

def similiarity_search(query: str, k=10):
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    try:
        db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
    
        relevant_response = db.similarity_search_with_relevance_scores(query, k=k)

    except Exception as e:
        print("Vector database not found")
        print(e)

    # responses = [chunk[0].page_content for chunk in relevant_response]
    # return responses
    print("Relevant response: ", relevant_response)

    print(f"\nSumber data: {[item[0].metadata['description'] for item in relevant_response]}") 
    return relevant_response

similiarity_search("rektor undiksha")
