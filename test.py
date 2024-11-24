from src.agents.query_expansion_agent import QueryExpansionAgent

question = "Apa perbedaan antara KRS dan KHS untuk MABA di FMIPA?"
expanded_question = QueryExpansionAgent.expand_query({"question": question})
print("Expanded Question:", expanded_question)