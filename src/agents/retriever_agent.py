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
        vector_from_query = embeddings.embed_query(query)
        state["vector_from_query"] = vector_from_query

        chunks_data = []

        try:
            vector_db_path = f"src/db/{vector_db_name}"
            db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
            relevant_response = db.similarity_search_with_score_by_vector(vector_from_query, k=candidates_size)
            faiss_index = db.index

            for doc, score in relevant_response:
                vector = faiss_index.reconstruct(doc.metadata['index'])
                chunks = {
                    "chunk": doc,
                    "score": score,
                    "vector": vector
                }
                chunks_data.append(chunks)
            
            state["chunks_data"] = chunks_data

            print("Relevant response: ", relevant_response)
            state["raw_context"] = relevant_response
            print(len(state["raw_context"]))
            print("-- RETRIEVER AGENT --\n\n")
            return state

        except Exception as e:
            print("Vector database not found")
            print("Error di Retriever Agent: ", str(e))
