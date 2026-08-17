from graph.state import AgroState
from Rag.vector_store import CustomVectorStore
from qdrant_client.http.models import Filter, FieldCondition, MatchValue


class RetrieveNode:
    def __init__(self):
        self.vectorstore = CustomVectorStore().vector_store()

    def run(self, state: AgroState):
        question = state.get("question", "")
        crop = state.get("crop", "").strip().lower()

        qdrant_filter = None
        if crop and crop != "unknown":
            qdrant_filter = Filter(
                must=[FieldCondition(key="metadata.crop", match=MatchValue(value=crop))]
            )

        docs = self.vectorstore.similarity_search(
            query=question,
            k=5,
            filter=qdrant_filter,
        )

        state["retrieved_docs"] = docs
        return state