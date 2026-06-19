from flask import Flask, render_template, request, jsonify
from google.genai import Client  # Importação direta e específica do Client
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

client = Client()

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def get_bot_response():
    user_message = request.json.get("message")

    try:
        # Envia a mensagem para a API do Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
        )
        
        # Retorna a resposta da IA em formato JSON
        return jsonify({"response": response.text})

    except Exception as e:
            print(f"Erro ao chamar a API do Gemini: {e}")
            return jsonify({"response": "Desculpe, ocorreu um erro ao processar sua mensagem."}), 500

#def home():
#    return "Olá! Seu ambiente Flask no VS Code está funcionando!"

if __name__ == "__main__":
    app.run(debug=True)