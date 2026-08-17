from Rag.loader import CustomPdfLoader
from Rag.vector_store import CustomVectorStore
from Rag.splitter import CustomTextSplitter


class IngestDocuments:

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.vectorstore = CustomVectorStore().vector_store()

    def ingest(self):
        loader = CustomPdfLoader(self.root_dir)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages/documents from {self.root_dir}")

        splitter = CustomTextSplitter(documents)
        split_docs = splitter.splitter()
        print(f"Split into {len(split_docs)} chunks")

        CustomVectorStore().add_documents(self.vectorstore, split_docs)
        print(f"Ingested {len(split_docs)} chunks into vector store.")


if __name__ == "__main__":
    IngestDocuments(root_dir="data/pdfs").ingest()