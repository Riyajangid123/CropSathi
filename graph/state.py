from typing import TypedDict


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