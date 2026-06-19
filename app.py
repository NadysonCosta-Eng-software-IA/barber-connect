from flask import Flask, render_template, request, jsonify
from google.genai import Client  # Importação direta e específica do Client
from flask_sqlalchemy import SQLAlchemy
from google.genai import types  # <-- IMPORTANTE: Adicione essa nova importação no topo do arquivo
from dotenv import load_dotenv

from datetime import datetime, timezone
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do Banco de Dados Neon (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o Banco de Dados
db = SQLAlchemy(app)

# Inicializa o Gemini
client = Client()


# ==========================================
# NOVOS MODELOS EXPANDIDOS (MULTI-TENANT + ESTOQUE)
# ==========================================

# 1. Tabela Principal: Cada barbearia que assinar seu sistema será um registro aqui
class Salao(db.Model):
    __tablename__ = 'saloes'
    id = db.Column(db.Integer, primary_key=True)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    cnpj_ou_cpf = db.Column(db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(20))
    
    # Relacionamentos
    clientes = db.relationship('Cliente', backref='salao', lazy=True)
    profissionais = db.relationship('Profissional', backref='salao', lazy=True)
    servicos = db.relationship('Servico', backref='salao', lazy=True)
    produtos = db.relationship('Produto', backref='salao', lazy=True)
    vendas = db.relationship('Venda', backref='salao', lazy=True)

# 2. Clientes (isolados por salão)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    salao_id = db.Column(db.Integer, db.ForeignKey('saloes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    agendamentos = db.relationship('Agenda', backref='cliente', lazy=True)

# 3. Profissionais/Barbeiros
class Profissional(db.Model):
    __tablename__ = 'profissionais'
    id = db.Column(db.Integer, primary_key=True)
    salao_id = db.Column(db.Integer, db.ForeignKey('saloes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100))
    agendamentos = db.relationship('Agenda', backref='profissional', lazy=True)

# 4. Serviços ofertados
class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    salao_id = db.Column(db.Integer, db.ForeignKey('saloes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao = db.Column(db.Integer) # em minutos
    agendamentos = db.relationship('Agenda', backref='servico', lazy=True)

# 5. Produtos para Venda e Estoque
class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    salao_id = db.Column(db.Integer, db.ForeignKey('saloes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, default=0)

# 6. Agendamentos da Barbearia
class Agenda(db.Model):
    __tablename__ = 'agenda'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Agendado") # Agendado, Concluído, Cancelado

# 7. Movimentação Financeira e Vendas (Produtos ou Serviços Concluídos)
class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    salao_id = db.Column(db.Integer, db.ForeignKey('saloes.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'Servico' ou 'Produto'
    valor_total = db.Column(db.Float, nullable=False)
    # A correção está aqui: usamos uma função lambda para pegar o horário UTC atualizado com timezone
    data_venda = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
    - Se perguntarem sobre horários, funcionamos de Segunda a Sábado, das 09h às 19h.
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
                temperature=0.5 # Controla a criatividade (0.5 é ótimo para conversas)
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