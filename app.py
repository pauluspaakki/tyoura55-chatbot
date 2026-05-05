from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG import build_vectorstore
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = Flask(__name__)
CORS(app)

# rakennetaan vectorstore erillisestä tiedostosta
vectorstore = build_vectorstore()

user_data = {}

# CHAT endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    user_id = data.get("user_id", "temp_user")

    print(f"Käyttäjän syöte: {user_input}")

    docs = vectorstore.similarity_search(
      user_input,
      k=3,
      filter={"user_id": user_id}
    )

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""

    ROOLI:
    Olet asiantunteva ja helposti lähestyttävä tekoälybotti yli 55-vuotiaiden työhyvinvoinnin ohjauksessa.

    TEHTÄVÄ:
    Toimi kahdessa eri tilanteessa:

    1) JOS aineistossa on käyttäjän lomaketuloksia (esim. numeroita 1–5 eri kategorioissa):
    → analysoi tulokset ja anna henkilökohtaista palautetta

    2) JOS lomaketuloksia EI ole:
    → vastaa käyttäjän kysymykseen normaalisti aineiston pohjalta

    LOMAKKEEN TULKINTA:
    - Tunnista kategoriat ja niiden keskiarvot (1–5)
    - 1–2 = hälyttävä → tarjoa konkreettinen neuvo
    - 3 = kohtalainen → anna kehitysehdotus
    - 4–5 = hyvä → kannusta

    ANALYYSIOHJEET:
    - Nosta esiin 2–3 tärkeintä huomiota
    - Älä listaa kaikkia arvoja, vaan tulkitse niitä
    - Puhu suoraan käyttäjälle ("Sinulla näyttää olevan...")
    - Ole kannustava, ei tuomitseva

    SÄÄNNÖT:
    1. Käytä vastauksen tietopohjana VAIN annettua aineistoa.
    2. ÄLÄ SISÄLLYTTÄÄ vastaukseen akateemisia lähdeviitteitä, vuosilukuja tai tutkijoiden nimiä (esim. jätä pois "van Laar ym." tai "(2017)").
    3. Puhu suoraan asiaa ja pidä kieli selkeänä suomenkielenä.
    4. Jos vastausta ei löydy aineistosta, sano ettet tiedä.
    5. Vastaa enintään viidellä lauseella ja käytä KAPPALEJAKOA kieliopillisesti oikein.
    6. Sävy: Keskusteleva, kannustava ja lämmin.

    AINEISTO:
    {context}

    KYSYMYS: {user_input}
    """

    from ollama import generate
    response = generate(model='Gemma2:9b', prompt=prompt)

    return jsonify({"response": response['response']})


# PDF UPLOAD endpoint
@app.route('/upload', methods=['POST'])

def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Ei tiedostoa"}), 400

    user_id = request.form.get("user_id", "temp_user")

    print("UPLOAD endpoint kutsuttu")

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Tyhjä tiedosto"}), 400

    filepath = "temp.pdf"
    file.save(filepath)

    loader = PyPDFLoader(filepath)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["type"] = "user_form"
        chunk.metadata["user.id"] = user_id

    vectorstore.add_documents(chunks)

    print("PDF LISÄTTY VECTORSTOREEN")

    os.remove(filepath)

    return jsonify({"message": "PDF on käsitelty onnistuneesti"}), 200

# chatin aloitus, START endpoint
@app.route('/start', methods=['GET'])
def start():
    return jsonify({
        "response": "Hei! Olen asiantuntijabotti työhyvinvoinnin ja -osaamisen edistämisessä.\n\n"
        " Voit lähettää pdf-tiedoston täyttämäsi kyselyn tuloksista klikkaamalla plussaa vasemmasta alakulmasta,"
        " tai voin vastata kysymyksiisi myös ilman tiedoston lähettämistä.\n\n"
        " Kertoisitko roolisi työelämässä ja miten voisin auttaa sinua?"
    })


if __name__ == '__main__':
    print("Serveri käynnissä: http://localhost:5000")
    app.run(port=5000)
