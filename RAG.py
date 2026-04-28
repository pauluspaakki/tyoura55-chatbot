import os
from config import URLS
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import UnstructuredURLLoader
# Varmista että URLS on määritelty täällä tai importattu
# from config import URLS

def build_vectorstore():
    persist_directory = "./chroma_db"
    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")

    # 1. TARKISTUS: Jos tietokanta on jo levyllä, älä lataa netistä mitään
    if os.path.exists(persist_directory):
        print("--- Tietokanta löytyi levyltä, ladataan se... ---")
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )

    # 2. LATAUS: Jos tietokantaa ei ole, ladataan aineisto netistä
    print("--- Tietokantaa ei löytynyt. Aloitetaan lataus (tämä kestää hetken)... ---")

    all_docs = []
    # Käytetään tässä aiempaa URLS-listaasi
    for i, url in enumerate(URLS):
        try:
            print(f"[{i+1}/{len(URLS)}] Ladataan: {url}")
            if url.lower().endswith(".pdf"):
                loader = PyPDFLoader(url)
            else:
                loader = WebBaseLoader(url)
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"Virhe ladattaessa {url}: {e}")

    # 3. PILKKOMINEN
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(all_docs)
    print(f"Luotiin {len(chunks)} tekstinpätkää.")

    # 4. TALLENNUS: Luodaan vektoriavaruus ja tallennetaan se levylle
    print("--- Luodaan embeddings ja tallennetaan levylle... ---")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory
    )

    print("VALMIS! Tietokanta on nyt tallennettu kansioon './chroma_db'")
    return vectorstore
