from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

DB_PATH = "app/rag/vectorstore"


def get_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

    return db.as_retriever(search_kwargs={"k": 3})


from functools import lru_cache

@lru_cache
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
