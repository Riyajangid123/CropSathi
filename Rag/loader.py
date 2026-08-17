from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path


class CustomPdfLoader:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def load(self):
        documents = []
        for file in self.data_path.rglob("*.pdf"):
            loader = PyMuPDFLoader(str(file))
            docs = loader.load()

            for doc in docs:
                doc.metadata.update({
                    "source": str(file),
                    "filename": file.name,
                    "crop": file.parent.name,
                })

            documents.extend(docs)
            print(f"Loaded {file.name} -> crop={file.parent.name}, {len(docs)} pages")

        return documents