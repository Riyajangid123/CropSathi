from Rag.vector_store import CustomVectorStore


class CustomRetriever:
    def __init__(self):
        self.vectorstore = CustomVectorStore().vector_store()

    def get_retriever(self):
        return self.vectorstore.as_retriever(search_kwargs={"k": 5})