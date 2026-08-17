from flashrank import Ranker, RerankRequest


class CustomReranker:

    def __init__(self):
        self.ranker = Ranker()

    def rerank(self, query, documents, top_k=3):

        passages = [
            {
                "id": i,
                "text": doc.page_content,
                "meta": doc.metadata
            }
            for i, doc in enumerate(documents)
        ]

        rerank_request = RerankRequest(
            query=query,
            passages=passages
        )

        results = self.ranker.rerank(rerank_request)

        top_results = results[:top_k]

        return [
            documents[result["id"]]
            for result in top_results
        ]