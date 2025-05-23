from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from src.models.carrinho import Carrinho, ItemCarrinho, db
from src.models.produto import Produto
from src.models.user import User
import json
import urllib.parse

carrinho_bp = Blueprint('carrinho', __name__)

@carrinho_bp.route('/carrinho')
def ver_carrinho():
    carrinho_id = session.get('carrinho_id')
    
    if not carrinho_id:
        return render_template('carrinho/carrinho.html', carrinho=None, itens=[], total=0)
    
    carrinho = Carrinho.query.get(carrinho_id)
    if not carrinho or carrinho.status != 'aberto':
        session.pop('carrinho_id', None)
        return render_template('carrinho/carrinho.html', carrinho=None, itens=[], total=0)
    
    admin = User.query.filter_by(username='admin').first()
    return render_template('carrinho/carrinho.html', carrinho=carrinho, itens=carrinho.itens, total=carrinho.total, admin=admin)

@carrinho_bp.route('/carrinho/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    produto_id = request.form.get('produto_id')
    quantidade = int(request.form.get('quantidade', 1))
    
    produto = Produto.query.get_or_404(produto_id)
    
    # Verificar se já existe um carrinho aberto na sessão
    carrinho_id = session.get('carrinho_id')
    
    if not carrinho_id:
        # Criar um novo carrinho
        admin = User.query.filter_by(username='admin').first()
        carrinho = Carrinho(
            cliente_nome='',
            cliente_telefone='',
            cliente_endereco='',
            taxa_entrega=admin.taxa_entrega,
            user_id=admin.id
        )
        db.session.add(carrinho)
        db.session.commit()
        
        session['carrinho_id'] = carrinho.id
    else:
        carrinho = Carrinho.query.get(carrinho_id)
        if not carrinho or carrinho.status != 'aberto':
            # Criar um novo carrinho se o atual não existir ou não estiver aberto
            admin = User.query.filter_by(username='admin').first()
            carrinho = Carrinho(
                cliente_nome='',
                cliente_telefone='',
                cliente_endereco='',
                taxa_entrega=admin.taxa_entrega,
                user_id=admin.id
            )
            db.session.add(carrinho)
            db.session.commit()
            
            session['carrinho_id'] = carrinho.id
    
    # Verificar se o produto já está no carrinho
    item_existente = ItemCarrinho.query.filter_by(carrinho_id=carrinho.id, produto_id=produto.id).first()
    
    if item_existente:
        # Atualizar quantidade
        item_existente.quantidade += quantidade
        item_existente.calcular_subtotal()
    else:
        # Adicionar novo item
        item = ItemCarrinho(
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=produto.preco * quantidade,
            carrinho_id=carrinho.id,
            produto_id=produto.id
        )
        db.session.add(item)
    
    db.session.commit()
    
    # Recalcular total do carrinho
    carrinho.calcular_total()
    db.session.commit()
    
    flash(f'{quantidade} unidade(s) de {produto.nome} adicionada(s) ao carrinho!', 'success')
    return redirect(url_for('carrinho.ver_carrinho'))

@carrinho_bp.route('/carrinho/atualizar/<int:item_id>', methods=['POST'])
def atualizar_item(item_id):
    quantidade = int(request.form.get('quantidade', 1))
    
    item = ItemCarrinho.query.get_or_404(item_id)
    carrinho = Carrinho.query.get(item.carrinho_id)
    
    # Verificar se o carrinho pertence à sessão atual
    if carrinho.id != session.get('carrinho_id'):
        flash('Erro ao atualizar o item.', 'danger')
        return redirect(url_for('carrinho.ver_carrinho'))
    
    if quantidade <= 0:
        db.session.delete(item)
    else:
        item.quantidade = quantidade
        item.calcular_subtotal()
    
    db.session.commit()
    
    # Recalcular total do carrinho
    carrinho.calcular_total()
    db.session.commit()
    
    flash('Carrinho atualizado com sucesso!', 'success')
    return redirect(url_for('carrinho.ver_carrinho'))

@carrinho_bp.route('/carrinho/remover/<int:item_id>', methods=['POST'])
def remover_item(item_id):
    item = ItemCarrinho.query.get_or_404(item_id)
    carrinho = Carrinho.query.get(item.carrinho_id)
    
    # Verificar se o carrinho pertence à sessão atual
    if carrinho.id != session.get('carrinho_id'):
        flash('Erro ao remover o item.', 'danger')
        return redirect(url_for('carrinho.ver_carrinho'))
    
    db.session.delete(item)
    db.session.commit()
    
    # Recalcular total do carrinho
    carrinho.calcular_total()
    db.session.commit()
    
    flash('Item removido do carrinho!', 'success')
    return redirect(url_for('carrinho.ver_carrinho'))

@carrinho_bp.route('/carrinho/finalizar', methods=['GET', 'POST'])
def finalizar_compra():
    carrinho_id = session.get('carrinho_id')
    
    if not carrinho_id:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('carrinho.ver_carrinho'))
    
    carrinho = Carrinho.query.get(carrinho_id)
    if not carrinho or carrinho.status != 'aberto' or not carrinho.itens:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('carrinho.ver_carrinho'))
    
    admin = User.query.filter_by(username='admin').first()
    
    if request.method == 'POST':
        carrinho.cliente_nome = request.form.get('nome')
        carrinho.cliente_telefone = request.form.get('telefone')
        carrinho.cliente_endereco = request.form.get('endereco')
        carrinho.status = 'finalizado'
        db.session.commit()
        
        # Gerar mensagem para WhatsApp
        mensagem = f"*Novo Pedido - Lea Rosa Laços*\n\n"
        mensagem += f"*Cliente:* {carrinho.cliente_nome}\n"
        mensagem += f"*Telefone:* {carrinho.cliente_telefone}\n"
        
        if carrinho.cliente_endereco:
            mensagem += f"*Endereço:* {carrinho.cliente_endereco}\n"
        
        mensagem += f"\n*Itens do Pedido:*\n"
        
        for item in carrinho.itens:
            mensagem += f"- {item.quantidade}x {item.produto.nome} - R$ {item.subtotal:.2f}\n"
        
        mensagem += f"\n*Taxa de Entrega:* R$ {carrinho.taxa_entrega:.2f}\n"
        mensagem += f"*Total:* R$ {carrinho.total:.2f}\n\n"
        
        # Adicionar informações de pagamento
        mensagem += f"*Pagamento via PIX:*\n"
        mensagem += f"Chave: {admin.chave_pix}\n"
        mensagem += f"Valor: R$ {carrinho.total:.2f}"
        
        # Codificar mensagem para URL do WhatsApp
        mensagem_codificada = urllib.parse.quote(mensagem)
        whatsapp_url = f"https://wa.me/{admin.whatsapp.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}?text={mensagem_codificada}"
        
        # Limpar sessão
        session.pop('carrinho_id', None)
        
        return render_template('carrinho/confirmacao.html', carrinho=carrinho, whatsapp_url=whatsapp_url, admin=admin)
    
    return render_template('carrinho/finalizar.html', carrinho=carrinho, admin=admin)

@carrinho_bp.route('/api/carrinho')
def api_carrinho():
    carrinho_id = session.get('carrinho_id')
    
    if not carrinho_id:
        return jsonify({"itens": [], "total": 0})
    
    carrinho = Carrinho.query.get(carrinho_id)
    if not carrinho or carrinho.status != 'aberto':
        return jsonify({"itens": [], "total": 0})
    
    return jsonify(carrinho.to_dict())
