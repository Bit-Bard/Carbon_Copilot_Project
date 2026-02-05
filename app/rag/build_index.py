import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


DATA_PATH = "data/company_docs"
DB_PATH = "app/rag/vectorstore"


def load_documents():
    docs = []

    for file in os.listdir(DATA_PATH):
        with open(os.path.join(DATA_PATH, file), "r", encoding="utf-8") as f:
            text = f.read()
            docs.append(Document(page_content=text))

    return docs


def build_index():

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(chunks, embeddings)

    db.save_local(DB_PATH)

    print("RAG index built successfully")


if __name__ == "__main__":
    build_index()
