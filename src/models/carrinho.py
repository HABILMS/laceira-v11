from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Carrinho(db.Model):
    __tablename__ = 'carrinhos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_telefone = db.Column(db.String(20), nullable=False)
    cliente_endereco = db.Column(db.Text, nullable=True)
    total = db.Column(db.Float, default=0.0)
    taxa_entrega = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='aberto')  # aberto, finalizado, cancelado
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    itens = db.relationship('ItemCarrinho', backref='carrinho', lazy=True, cascade="all, delete-orphan")
    
    def calcular_total(self):
        total_itens = sum(item.subtotal for item in self.itens)
        self.total = total_itens + self.taxa_entrega
        return self.total
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_nome': self.cliente_nome,
            'cliente_telefone': self.cliente_telefone,
            'cliente_endereco': self.cliente_endereco,
            'total': self.total,
            'taxa_entrega': self.taxa_entrega,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'status': self.status,
            'user_id': self.user_id,
            'itens': [item.to_dict() for item in self.itens]
        }

class ItemCarrinho(db.Model):
    __tablename__ = 'itens_carrinho'
    
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, default=1)
    preco_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    carrinho_id = db.Column(db.Integer, db.ForeignKey('carrinhos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    produto = db.relationship('Produto')
    
    def calcular_subtotal(self):
        self.subtotal = self.quantidade * self.preco_unitario
        return self.subtotal
    
    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
            'subtotal': self.subtotal,
            'produto': self.produto.to_dict() if self.produto else None
        }
