from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    instagram = db.Column(db.String(100), nullable=True)
    taxa_entrega = db.Column(db.Float, default=0.0)
    chave_pix = db.Column(db.String(100), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'telefone': self.telefone,
            'whatsapp': self.whatsapp,
            'instagram': self.instagram,
            'taxa_entrega': self.taxa_entrega,
            'chave_pix': self.chave_pix
        }
