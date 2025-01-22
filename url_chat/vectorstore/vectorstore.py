from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def create_vector_store(self, folder_path):
        loader = DirectoryLoader(folder_path, loader_cls=TextLoader)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(split_docs, self.embeddings)
        return vector_store

    def save_vector_store(self, vector_store, path="faiss_store"):
        vector_store.save_local(path)

    def load_vector_store(self, path="faiss_store"):
        return FAISS.load_local(path, self.embeddings)