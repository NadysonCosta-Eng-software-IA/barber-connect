from app import app, db

print("Conectando ao Neon e criando as tabelas...")

with app.app_context():
    db.create_all()

print("Tabelas criadas com sucesso no seu banco online!")