from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from src.models.produto import Produto, db
from src.models.user import User
from src.routes.auth import login_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

produtos_bp = Blueprint('produtos', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@produtos_bp.route('/admin/produtos')
@login_required
def listar_produtos():
    produtos = Produto.query.filter_by(user_id=request.cookies.get('user_id')).all()
    return render_template('admin/produtos/listar.html', produtos=produtos)

@produtos_bp.route('/admin/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        colecao = request.form.get('colecao')
        descricao = request.form.get('descricao')
        preco = float(request.form.get('preco'))
        
        produto = Produto(
            nome=nome,
            colecao=colecao,
            descricao=descricao,
            preco=preco,
            user_id=request.cookies.get('user_id')
        )
        
        # Processar imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Gerar nome único para evitar conflitos
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                produto.imagem = f"/static/uploads/{unique_filename}"
        
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('produtos.listar_produtos'))
    
    return render_template('admin/produtos/novo.html')

@produtos_bp.route('/admin/produtos/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    # Verificar se o produto pertence ao usuário logado
    if produto.user_id != int(request.cookies.get('user_id')):
        flash('Você não tem permissão para editar este produto.', 'danger')
        return redirect(url_for('produtos.listar_produtos'))
    
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.colecao = request.form.get('colecao')
        produto.descricao = request.form.get('descricao')
        produto.preco = float(request.form.get('preco'))
        produto.disponivel = 'disponivel' in request.form
        
        # Processar imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Gerar nome único para evitar conflitos
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Remover imagem antiga se existir
                if produto.imagem:
                    old_image_path = os.path.join(current_app.root_path, produto.imagem.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                produto.imagem = f"/static/uploads/{unique_filename}"
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos.listar_produtos'))
    
    return render_template('admin/produtos/editar.html', produto=produto)

@produtos_bp.route('/admin/produtos/excluir/<int:produto_id>', methods=['POST'])
@login_required
def excluir_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    # Verificar se o produto pertence ao usuário logado
    if produto.user_id != int(request.cookies.get('user_id')):
        flash('Você não tem permissão para excluir este produto.', 'danger')
        return redirect(url_for('produtos.listar_produtos'))
    
    # Remover imagem se existir
    if produto.imagem:
        image_path = os.path.join(current_app.root_path, produto.imagem.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(produto)
    db.session.commit()
    
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('produtos.listar_produtos'))

@produtos_bp.route('/api/produtos')
def api_produtos():
    produtos = Produto.query.filter_by(disponivel=True).all()
    return jsonify([produto.to_dict() for produto in produtos])

@produtos_bp.route('/api/produtos/<int:produto_id>')
def api_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    return jsonify(produto.to_dict())
