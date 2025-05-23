import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db, User
from src.models.produto import Produto
from src.models.carrinho import Carrinho, ItemCarrinho
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Garantir que a pasta de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Importar blueprints
from src.routes.auth import auth_bp
from src.routes.produtos import produtos_bp
from src.routes.carrinho import carrinho_bp
from src.routes.admin import admin_bp

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(carrinho_bp)
app.register_blueprint(admin_bp)

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()
    
    # Verificar se já existe um usuário admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            nome='Lea Rosa',
            telefone='67984494746',
            whatsapp='67984494746',
            instagram='learosaacesorios',
            taxa_entrega=10.0,
            chave_pix='67984494746'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    produtos = Produto.query.filter_by(disponivel=True).order_by(Produto.data_criacao.desc()).limit(8).all()
    admin = User.query.filter_by(username='admin').first()
    return render_template('index.html', produtos=produtos, admin=admin)

@app.route('/catalogo')
def catalogo():
    produtos = Produto.query.filter_by(disponivel=True).all()
    admin = User.query.filter_by(username='admin').first()
    return render_template('catalogo.html', produtos=produtos, admin=admin)

@app.route('/produto/<int:produto_id>')
def produto_detalhe(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    admin = User.query.filter_by(username='admin').first()
    return render_template('produto_detalhe.html', produto=produto, admin=admin)

@app.route('/sobre')
def sobre():
    admin = User.query.filter_by(username='admin').first()
    return render_template('sobre.html', admin=admin)

@app.route('/contato')
def contato():
    admin = User.query.filter_by(username='admin').first()
    return render_template('contato.html', admin=admin)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
