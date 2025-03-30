from langgraph.graph import END, START, StateGraph
from src.state import AgentState
from src.agents import QueryExpansionAgent, RetrievalAgent, CorrectiveAgent, GeneratorAgent

def build_graph(question: str, vector_db_name: str, embedder_model: str, llm_model: str, candidates_size: int):
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("query_expansion_agent", QueryExpansionAgent.expand_query)
    workflow.add_node("retriever_agent", RetrievalAgent.similiarity_search)
    workflow.add_node("corrective_agent", CorrectiveAgent.correct)
    workflow.add_node("generator_agent", GeneratorAgent.generate)

    workflow.add_edge(START, "query_expansion_agent")
    workflow.add_edge("query_expansion_agent", "retriever_agent")
    workflow.add_edge("retriever_agent", "corrective_agent")
    workflow.add_edge("corrective_agent", "generator_agent")
    workflow.add_edge("generator_agent", END)

    graph = workflow.compile()
    result = graph.invoke({
        "question": question, 
        "vector_db_name": vector_db_name, 
        "embedder_model": embedder_model, 
        "llm_model": llm_model,
        "candidates_size": candidates_size
    })

    print(result)

    return result

from src.naive_rag.retriever import Retriever
from src.naive_rag.generator import Generator 

def build_naive_rag(question: str, vector_db_name: str, embedder_model: str, llm_model: str, candidates_size: int):
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("retriever", Retriever.similiarity_search)
    workflow.add_node("generator", Generator.generate)

    # Add Edge
    workflow.add_edge(START, "retriever")
    workflow.add_edge("retriever", "generator")
    workflow.add_edge("generator", END)

    graph = workflow.compile()
    result = graph.invoke({
        "question": question, 
        "vector_db_name": vector_db_name, 
        "embedder_model": embedder_model, 
        "llm_model": llm_model,
        "candidates_size": candidates_size
    })

    print(result["final_answer"])

    return result

conf = {
    "question": "kapan jadwal kkn 2025",
    "vector_db_name": "db_20250223_203128",
    "embedder_model": "text-embedding-3-small",
    "llm_model": "gpt-4o-mini",
    "candidates_size": 15
}

# response = build_graph(**conf)
# print(response)



    




        

    


