from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from src.state import AgentState
import os

load_dotenv()

# Load embedding model
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

class RetrieverAgent:
    def similiarity_search(state: AgentState):
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        try:
            db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
        
            relevant_response = db.similarity_search_with_relevance_scores(state["expanded_question"], k=10)

        except Exception as e:
            print("Vector database not found")
            print(e)

        # responses = [chunk[0].page_content for chunk in relevant_response]
        # return responses
        print("Relevant response: ", relevant_response)

        data_source = [item[0].metadata['description'] for item in relevant_response]

        unique_data_source = []
        for item in data_source:
            if item not in unique_data_source:
                unique_data_source.append(item)

        data_source = unique_data_source

        print(f"\nSumber data: {data_source}") 
        return relevant_response