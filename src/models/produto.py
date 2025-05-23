from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    colecao = db.Column(db.String(100), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(255), nullable=True)
    disponivel = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'colecao': self.colecao,
            'descricao': self.descricao,
            'preco': self.preco,
            'imagem': self.imagem,
            'disponivel': self.disponivel,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y'),
            'user_id': self.user_id
        }
