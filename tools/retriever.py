from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def similiarity_search(query: str, k=4):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
    
        relevant_response = db.similarity_search_with_relevance_scores(query, k=20)

    except Exception as e:
        print("Vector database not found")
        print(e)

    # responses = [chunk[0].page_content for chunk in relevant_response]
    # return responses
    print("Relevant response: ", relevant_response)
    return relevant_response

