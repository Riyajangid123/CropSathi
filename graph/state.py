from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages


class AgroState(TypedDict, total=False):
    image: object
    question: str
    language: str
    crop: str

    disease: str
    confidence: float
    observations: str

    retrieved_docs: list
    reranked_docs: list
    context: str

    answer: str

    needs_retrieval: bool
    diagnosis_uncertain: bool

    messages: Annotated[list, add_messages]