from Rag.reranker import CustomReranker
from graph.state import AgroState


class RerankNode:

    def __init__(self):
        self.reranker = CustomReranker()
        

    def run(self, state: AgroState):

        documents = state["retrieved_docs"]
        query="""Crop: {state.get("crop", "")}
                
                Disease: {state.get("disease", "")}
                
                Symptoms:{state.get("observations", "")}
                
                Farmer Question:{state.get("question", "")}
            """

        reranked_docs = self.reranker.rerank(
            query=query,
            documents=documents,
            top_k=3
        )

        return {
            **state,
            "reranked_docs": reranked_docs
        }