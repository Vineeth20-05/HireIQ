from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

vector_store = Chroma(
    client=client,
    collection_name="resumes",
    embedding_function=embedding_model
)