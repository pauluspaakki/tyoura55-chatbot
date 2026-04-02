from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG import build_vectorstore

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
    Olet asiantuntija ikäjohtamisessa. Käytä alla olevaa lähdeaineistoa vastaamaan kysymykseen.
    Jos vastausta ei löydy aineistosta, sano ettet tiedä, älä keksi omia.
    Tervehdi ystävällisesti, vastaa suomeksi ja enintään viidellä lauseella.

    {context}

    Kysymys: {user_input}
    """

    from ollama import generate
    response = generate(model='llama3', prompt=prompt)

    return jsonify({"response": response['response']})


if __name__ == '__main__':
    print("Serveri käynnissä: http://localhost:5000")
    app.run(port=5000)