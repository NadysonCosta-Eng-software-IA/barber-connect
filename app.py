from flask import Flask, render_template, request, jsonify
from google.genai import Client  # Importação direta e específica do Client
from dotenv import load_dotenv
from google.genai import types  # <-- IMPORTANTE: Adicione essa nova importação no topo do arquivo
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

    # 1. Defina o comportamento do seu robô aqui
    instrucao_barbearia = """
    Você é o "Guto", um barbeiro e atendente virtual muito gente boa, carismático e profissional da barbearia "BarbeConnect".
    Seu objetivo é ajudar os clientes a entenderem os serviços, preços e dar dicas de estilo.

    Regras de comportamento:
    - Seja sempre amigável, use gírias leves de barbeiro se achar adequado (ex: "Fala, meu consagrado!", "Fala, chefe!", "Tudo tranquilo?").
    - Use emojis para deixar a conversa descontraída.
    - Nossos serviços principais são: Cabelo (R$ 40), Barba (R$ 30) e o Combo Cabelo + Barba (R$ 60).
    - Se perguntarem sobre horários, funcionamos de Terça a Sábado, das 09h às 19h.
    - Se o cliente quiser agendar, diga de forma simpática para ele informar o dia e o horário desejado (ou simule que está anotando).
    - Seja breve e direto nas respostas, imitando uma conversa real de WhatsApp. Não mande textos gigantes.
    """


    try:
        # Envia a mensagem para a API do Gemini
        # 2. Enviamos a instrução dentro do parâmetro 'config'
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=instrucao_barbearia,
                temperature=0.7 # Controla a criatividade (0.7 é ótimo para conversas)
            )
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