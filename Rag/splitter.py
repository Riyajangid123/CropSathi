from langchain_text_splitters import RecursiveCharacterTextSplitter

class CustomTextSplitter:
    def __init__(self,documents):
        self.documents=documents

    def splitter(self):
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        split_docs=text_splitter.split_documents(self.documents)
        
        return split_docs