# Lataus + chunkkaus + vektorit
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from config import URLS

# Voidaanko ladata levylle ? 

def build_vectorstore():
    print("--- VAIHE 1: Ladataan sivut ---")

    all_docs = []
    for i, url in enumerate(URLS):
        try:
            print(f"[{i+1}/{len(URLS)}] {url}")
            loader = WebBaseLoader(url)
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"Virhe: {e}")

    print(f"Dokumentteja: {len(all_docs)}")

    print("\n--- VAIHE 2: Pilkotaan ---")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(all_docs)
    print(f"Chunkkeja: {len(chunks)}")

    print("\n--- VAIHE 3: Embeddings ---")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="mxbai-embed-large")
    )

    print("VALMIS!")
    return vectorstore