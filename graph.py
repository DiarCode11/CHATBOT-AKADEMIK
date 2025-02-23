from langgraph.graph import END, START, StateGraph
from src.state import AgentState
from src.agents import QueryExpansionAgent, RetrieverAgent, CorrectiveAgent, GeneratorAgent

def build_graph(question: str, vector_db_name: str, embedder_model: str, llm_model: str, candidates_size: int):
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("query_expansion_agent", QueryExpansionAgent.expand_query)
    workflow.add_node("retriever_agent", RetrieverAgent.similiarity_search)
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

    print(result["final_answer"])

    all_result = {
        
    }

    return result["final_answer"]
    


# data = build_graph("siapa rektor undiksha", "db_20250221_000015", "text-embedding-3-small", "gpt-4o-mini", 5)
# print(data)


        

    


