from langgraph.graph import END, START, StateGraph
from src.state import AgentState
from src.agents import QueryExpansionAgent, RetrieverAgent, CorrectiveAgent, GeneratorAgent

def build_graph(question: str):
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
    result = graph.invoke({"question": question})

    print(result["final_answer"])

    return result["final_answer"]
    


build_graph("kapan jadwal menyusun krs 2025")


        

    


