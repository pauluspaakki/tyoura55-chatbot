from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG import build_vectorstore
import os
#import libvoikko

app = Flask(__name__)
CORS(app)

# rakennetaan vectorstore erillisestä tiedostosta
vectorstore = build_vectorstore()

user_states = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    user_id = data.get('user_id', 'default')

    print(f"Käyttäjän syöte: {user_input}")

    state = user_states.get(user_id, "start")

    if state == "start":
        user_states[user_id] = "waiting_choice"

        return jsonify({
            "response": "Haluatko keskustella täyttämäsi kyselyn tuloksista? (kyllä/ei)"
        })

    if state == "waiting_choice":
        if user_input.lower() == "kyllä":
            user_states[user_id] = "waiting_pdf"

            return jsonify({
                "response": "Lähetä pdf-tiedosto"
            })

        else:
            user_states[user_id] = "normal_chat"

            return jsonify({
                "response": "Selvä! Mitä haluaisit kysyä?"
            })

    if state == "normal_chat":
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

    if state == "waiting_pdf":
        return jsonify({
            "response": "Ole hyvä ja lähetä pdf-tiedosto."
        })

    return jsonify({"response": "Virhe tilassa."})

@app.route('/upload', methods=['POST'])
def upload_pdf():
    user_id = request.form.get("user_id", "default")

    if 'file' not in request.files:
        return jsonify({"error": "Ei tiedostoa"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Tyhjä tiedosto"}), 400

    filepath = "temp.pdf"
    file.save(filepath)

    print("Pdf vastaanotettu")

    if os.path.exists(filepath):
        os.remove(filepath)

    user_states[user_id] = "normal_chat"

    return jsonify({
        "response": "Pdf vastaanotettu! Mitä haluaisit kysyä?"
    })


if __name__ == '__main__':
    print("Serveri käynnissä: http://localhost:5000")
    app.run(port=5000)
