from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG import build_vectorstore
#import libvoikko

app = Flask(__name__)
CORS(app)


# MUUTOS:
# rakennetaan vectorstore erillisestä tiedostosta
vectorstore = build_vectorstore()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    print(f"Kysymys: {user_input}")

    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""

   ROOLI:
    Olet asiantunteva ja helposti lähestyttävä tekoälybotti yli 55-vuotiaiden työhyvinvoinnin ohjauksessa.

    TEHTÄVÄ:
    Vastaa käyttäjän kysymykseen hyödyntäen annettua aineistoa.

    SÄÄNNÖT:
    1. Käytä vastauksen tietopohjana VAIN annettua aineistoa.
    2. ÄLÄ SISÄLLYTTÄÄ vastaukseen akateemisia lähdeviitteitä, vuosilukuja tai tutkijoiden nimiä (esim. jätä pois "van Laar ym." tai "(2017)").
    3. Puhu suoraan asiaa ja pidä kieli selkeänä suomen kielenä.
    4. Jos vastausta ei löydy aineistosta, sano ettet tiedä.
    5. Vastaa enintään viidellä lauseella ja käytä kappalejakoa.
    6. Sävy: Keskusteleva, kannustava ja lämmin.


    {context}

    Kysymys: {user_input}
    """

    from ollama import generate
    response = generate(model='Gemma2:9b', prompt=prompt)

    return jsonify({"response": response['response']})


if __name__ == '__main__':
    print("Serveri käynnissä: http://localhost:5000")
    app.run(port=5000)