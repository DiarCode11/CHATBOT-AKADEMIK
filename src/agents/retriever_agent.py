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

        embedder = state["embedder_model"]
        vector_db_name = state["vector_db_name"]
        candidates_size = state['candidates_size']

        embeddings = OpenAIEmbeddings(model=embedder)
        query = state["expanded_question"]

        try:
            vector_db_path = f"d:/SKRIPSI/CHATBOT AKADEMIK/src/db/{vector_db_name}"
            db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
            relevant_response = db.similarity_search(query, k=candidates_size)
            print("Relevant response: ", relevant_response)
            state["raw_context"] = relevant_response
            print("-- RETRIEVER AGENT --\n\n")
            return state

        except Exception as e:
            print("Vector database not found")
            print("Error di Retriever Agent: ", str(e))
