from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.models.user import User, db
from src.routes.auth import login_required
import qrcode
import base64
import io
import re

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('admin/dashboard.html', user=user)

@admin_bp.route('/admin/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.nome = request.form.get('nome')
        user.telefone = request.form.get('telefone')
        user.whatsapp = request.form.get('whatsapp')
        user.instagram = request.form.get('instagram')
        user.taxa_entrega = float(request.form.get('taxa_entrega'))
        user.chave_pix = request.form.get('chave_pix')
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.configuracoes'))
    
    return render_template('admin/configuracoes.html', user=user)

@admin_bp.route('/gerar-pix/<float:valor>')
def gerar_pix(valor):
    admin = User.query.filter_by(username='admin').first()
    
    # Limpar a chave PIX (remover caracteres não numéricos se for um telefone)
    chave_pix = re.sub(r'[^0-9]', '', admin.chave_pix)
    
    # Gerar QR code para PIX
    pix_payload = f"00020126330014BR.GOV.BCB.PIX01110{len(chave_pix)}{chave_pix}52040000530398654{valor:.2f}5802BR5913{admin.nome}6008SAOPAULO62070503***6304"
    
    img = qrcode.make(pix_payload)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('pix/qrcode.html', 
                          qrcode_data=img_str, 
                          valor=valor, 
                          chave_pix=admin.chave_pix,
                          admin=admin)
