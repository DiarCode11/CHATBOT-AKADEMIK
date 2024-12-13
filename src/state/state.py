from typing_extensions import TypedDict, Literal, Optional, Annotated, Sequence

class AgentState(TypedDict):
    question : Optional[str]= None
    data_source : Optional[str]= None
    expanded_question : Optional[str]= None
    raw_context : Optional[str]= None
    cleaned_context : Optional[str]= None
    final_answer : Optional[str]= None
