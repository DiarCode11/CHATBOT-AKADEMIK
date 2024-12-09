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
            vector_db_path = os.path.join(os.path.dirname(__file__), "..", "..", "vector_db")
            db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
        
            relevant_response = db.similarity_search_with_relevance_scores(query, k=15)

        except Exception as e:
            print("Vector database not found")
            print(e)

        # responses = [chunk[0].page_content for chunk in relevant_response]
        # return responses
        # print("Relevant response: ", relevant_response)

        data_source = [item[0].metadata['description'] for item in relevant_response]

        unique_data_source = []
        for item in data_source:
            if item not in unique_data_source:
                unique_data_source.append(item)
        data_source = unique_data_source

        state["raw_context"] = [{"informasi": item[0].page_content, "tahun publikasi informasi": item[0].metadata["year"]} for item in relevant_response]
        state["data_source"] = data_source

        print("-- RETRIEVER AGENT --")

        return state