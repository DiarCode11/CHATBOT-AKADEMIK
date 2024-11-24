from typing_extensions import TypedDict, Literal, Optional, Annotated, Sequence

class AgentState(TypedDict):
    question : Optional[str]= None
    expanded_question : Optional[str]= None
    answer : Optional[str]= None
