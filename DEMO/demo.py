import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# 1. LISTAURL-OSOITTEET (Siivottu duplikaateista)
urls = list(set([
    "https://sites.tuni.fi/tamk-julkaisut/terveys/hyvat-kaytannot-yli-50-vuotiaiden-tyoura-ja-ikajohtamiseen-yamk-opinnaytetoissa-paivi-heimonen-ja-eeva-liikanen/",
    "https://sites.tuni.fi/tamk-julkaisut/terveys/yli-55-vuotiaiden-tyourajohtaminen-tarkastelussa-tulevaisuuden-tyoelamataidot-ja-osaaminen-paivi-heimonen-ja-eeva-liikanen/",
    "https://doi.org/10.1016/j.apergo.2020.103082",
    "https://doi.org/10.3390/ijerph18115626",
    "https://urn.fi/URN:ISBN:978-951-691-367-7",
    "https://www.who.int/news-room/fact-sheets/detail/ageing-and-health",
    "https://doi.org/10.1002/puh2.70130",
    "https://urn.fi/URN:NBN:fi:amk-2021090517447",
    "https://urn.fi/URN:NBN:fi:amk-202502172975",
    "https://urn.fi/URN:NBN:fi:amk-2023052614456",
    "https://urn.fi/URN:NBN:fi:amk-202505038802",
    "https://urn.fi/URN:NBN:fi:amk-2021061215851",
    "https://urn.fi/URN:NBN:fi:amk-2021061015595",
    "https://urn.fi/URN:NBN:fi:amk-2022060716035",
    "https://www.theseus.fi/handle/10024/860837",
    "https://urn.fi/URN:NBN:fi:amk-202205098131",
    "https://urn.fi/URN:NBN:fi:amk-2024112830893",
    "https://urn.fi/URN:NBN:fi:amk-2023051711479",
    "https://urn.fi/URN:NBN:fi:amk-2025052515728",
    "https://urn.fi/URN:NBN:fi:amk-2025092525068",
    "https://urn.fi/URN:ISBN:978-952-261-997-6",
    "https://pelitutkimus.journal.fi/article/view/108008",
    "https://doi.org/10.1007/s10902-017-9869-7",
    "https://doi.org/10.1016/j.chb.2017.03.010"
]))

# 1. MATERIAALIEN LATAUS (Yksitellen virheiden välttämiseksi)
print("--- VAIHE 1: Aloitetaan sivujen lataus ---")
all_docs = []
for i, url in enumerate(urls):
    try:
        print(f"[{i+1}/{len(urls)}] Ladataan: {url}")
        loader = WebBaseLoader(url)
        all_docs.extend(loader.load())
    except Exception as e:
        print(f"SKIPPATAAN (Virhe ladattaessa {url}): {e}")

print(f"\nLataus valmis. Dokumentteja onnistuttiin hakemaan: {len(all_docs)}")

# 2. PILKKOMINEN
print("\n--- VAIHE 2: Pilkotaan teksti osiin ---")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(all_docs)
print(f"Luotu {len(chunks)} tekstipalaa.")

# 3. VEKTORITIETOKANTA (Käytetään mxbai-mallia nopeuden takia)
print("\n--- VAIHE 3: Luodaan vektoritietokanta (Embeddings) ---")
print("Huom: Jos tämä jumittaa, varmista että olet ajanut 'ollama pull mxbai-embed-large'")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="mxbai-embed-large")
)
print("Vektorointi VALMIS!")

# 4. HAKU- JA VASTAUSLOGIIKKA
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    print(f"Kysymys vastaanotettu: {user_input}")

    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Olet asiantuntija ikäjohtamisessa. Käytä alla olevaa lähdeaineistoa vastaamaan kysymykseen.
    Jos vastausta ei löydy aineistosta, sano ettet tiedä, älä keksi omia.
    Referoi aineistoa, mutta älä esittäydy aineiston henkilöinä.
    Vastaa suomeksi ja enintään 1-7 lauseella.

    LÄHDEAINEISTO:
    {context}

    KYSYMYS: {user_input}
    """

    from ollama import generate
    response = generate(model='llama3', prompt=prompt)
    return jsonify({"response": response['response']})

if __name__ == '__main__':
    print("\n--- KAIKKI VALMISTA ---")
    print("RAG-palvelin käynnissä portissa 5000...")
    app.run(port=5000)