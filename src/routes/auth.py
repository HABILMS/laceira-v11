from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.models.user import User, db
from werkzeug.security import check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha incorretos. Tente novamente.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.nome = request.form.get('nome')
        user.telefone = request.form.get('telefone')
        user.whatsapp = request.form.get('whatsapp')
        user.instagram = request.form.get('instagram')
        user.taxa_entrega = float(request.form.get('taxa_entrega'))
        user.chave_pix = request.form.get('chave_pix')
        
        # Verificar se a senha foi alterada
        nova_senha = request.form.get('nova_senha')
        if nova_senha and len(nova_senha) >= 6:
            user.set_password(nova_senha)
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/perfil.html', user=user)
