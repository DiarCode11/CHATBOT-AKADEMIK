from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from src.state import AgentState
import os

class RetrieverAgent:
    @staticmethod
    def similiarity_search(state: AgentState):
        # Load embedding model
        load_dotenv()

        EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

        query = state["expanded_question"]

        try:
            vector_db_path = "d:/SKRIPSI/CHATBOT AKADEMIK/src/db/db_20250210_142509"
            
            db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
        
            relevant_response = db.similarity_search(query, k=15)

            print("Relevant response: ", relevant_response)

        except Exception as e:
            print("Vector database not found")
            print(e)

        state["raw_context"] = relevant_response

        print("-- RETRIEVER AGENT --\n\n")

        return state