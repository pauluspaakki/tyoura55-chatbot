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


    TEHTÄVÄ:
    Vastaa käyttäjän kysymykseen käyttäen annettua aineistoa. Noudata sääntöjä.

    SÄÄNNÖT:
    Käytä VAIN annettua lähdeaineistoa, älä käytä omaa tietämystäsi
    Jos vastausta ei löydy, sano ettet tiedä
    Vastaa enintään viidellä lauseella
    Käytä kappalejakoa
    Pidä sävy keskustelevana
    Perustele vastauksesi lyhyesti
    Vastaa AINA suomeksi


    {context}

    Kysymys: {user_input}
    """

    from ollama import generate
    response = generate(model='Gemma2:9b', prompt=prompt)

    return jsonify({"response": response['response']})


if __name__ == '__main__':
    print("Serveri käynnissä: http://localhost:5000")
    app.run(port=5000)