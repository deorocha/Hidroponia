# login.py

import streamlit as st
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from contextlib import closing

# Configurações
DB_NAME = "./dados/hidroponia.db"
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465
SMTP_USER = "contato@horta.tec.br"
SMTP_PASSWORD = "Vcqr1264#"
APP_URL = "http://localhost:8501"

# Inicializar banco de dados
def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_usuarios (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                verified INTEGER DEFAULT 0,
                confirmation_token TEXT,
                token_expiration TEXT
            )
        ''')
        conn.commit()

# Gerar hash da senha
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return salt, hashed.hex()

# Verificar credenciais
def verify_credentials(login, password):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT password, salt, verified FROM tbl_usuarios WHERE login = ?
        ''', (login,))
        result = cursor.fetchone()
        
        if result:
            stored_hash, salt, verified = result
            _, input_hash = hash_password(password, salt)
            if input_hash == stored_hash and verified == 1:
                return True
        return False

# Cadastrar novo usuário
def register_user(user_name, login, email, password):
    salt, hashed_password = hash_password(password)
    token = secrets.token_urlsafe(32)
    expiration = (datetime.now() + timedelta(hours=24)).isoformat()
    
    try:
        with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tbl_usuarios 
                (user_name, login, password, salt, email, verified, confirmation_token, token_expiration)
                VALUES (?, ?, ?, ?, ?, 0, ?, ?)
            ''', (user_name, login, hashed_password, salt, email, token, expiration))
            conn.commit()
        return token
    except sqlite3.IntegrityError:
        return None

# Enviar e-mail de confirmação
def send_confirmation_email(email, token):
    confirmation_link = f"{APP_URL}?token={token}"
    
    message = MIMEText(f"""
    <html>
        <body>
            <h2>Confirmação de Cadastro</h2>
            <p>Clique no link abaixo para confirmar seu e-mail:</p>
            <p><a href="{confirmation_link}">Confirmar E-mail</a></p>
            <p>Se você não solicitou este cadastro, ignore este e-mail.</p>
        </body>
    </html>
    """, "html")
    
    message["Subject"] = "Confirmação de Cadastro"
    message["From"] = SMTP_USER
    message["To"] = email
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {str(e)}")
        return False

# Verificar token de confirmação
def verify_token(token):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, token_expiration FROM tbl_usuarios 
            WHERE confirmation_token = ? AND verified = 0
        ''', (token,))
        result = cursor.fetchone()
        
        if result:
            user_id, expiration_str = result
            expiration = datetime.fromisoformat(expiration_str)
            if datetime.now() < expiration:
                cursor.execute('''
                    UPDATE tbl_usuarios 
                    SET verified = 1, 
                        confirmation_token = NULL,
                        token_expiration = NULL
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
        return False

# Interface principal
def main():
    # Cabeçalho ultra compacto
    st.markdown("<h2 style='margin-top:0; padding-top:0; margin-bottom:0;'>🌿 HortaTec</h2>", 
                unsafe_allow_html=True)
    init_db()
    
    # Verificar token na URL
    query_params = st.query_params.to_dict()
    if 'token' in query_params:
        token = query_params['token']
        if verify_token(token):
            st.success("E-mail confirmado com sucesso! Agora você pode fazer login.")
        else:
            st.error("Token inválido ou expirado.")
        # Remove o token da URL
        st.query_params.clear()
    
    # Popup de login
    if st.session_state.show_login:
        with st.popover("Acesso ao Sistema", use_container_width=True):
            st.subheader("Login")
            
            with st.form("login_form"):
                login = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar")
                
                if submit:
                    if verify_credentials(login, password):
                        with closing(sqlite3.connect(DB_NAME)) as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                SELECT user_id, user_name FROM tbl_usuarios WHERE login = ?
                            ''', (login,))
                            result = cursor.fetchone()
                            
                        if result:
                            st.session_state.user_id = result[0]
                            st.session_state.user_name = result[1]
                            st.session_state.logged_in = True
                            st.session_state.show_login = False
                            st.success("Login realizado com sucesso!")
                            st.rerun()
                    else:
                        st.error("Credenciais inválidas ou e-mail não confirmado")
            
            if st.button("Cadastrar novo usuário"):
                st.session_state.show_login = False
                st.session_state.show_signup = True
                st.rerun()

    # Popup de cadastro
    if st.session_state.show_signup:
        with st.popover("Cadastro de Usuário", use_container_width=True):
            st.subheader("Novo Cadastro")
            
            with st.form("signup_form"):
                user_name = st.text_input("Nome Completo")
                login = st.text_input("Nome de Usuário")
                email = st.text_input("E-mail")
                password = st.text_input("Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                submit_signup = st.form_submit_button("Criar Conta")
                
                if submit_signup:
                    if password != confirm_password:
                        st.error("As senhas não coincidem")
                    elif not user_name or not login or not email or not password:
                        st.error("Todos os campos são obrigatórios")
                    elif len(password) < 8:
                        st.error("A senha deve ter pelo menos 8 caracteres")
                    else:
                        token = register_user(user_name, login, email, password)
                        if token:
                            if send_confirmation_email(email, token):
                                st.success("Cadastro realizado! Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada.")
                                st.session_state.show_signup = False
                                st.session_state.show_login = True
                                st.rerun()
                            else:
                                st.error("Falha ao enviar e-mail de confirmação")
                        else:
                            st.error("Usuário ou e-mail já cadastrado")
            
            if st.button("Voltar para Login"):
                st.session_state.show_signup = False
                st.session_state.show_login = True
                st.rerun()

    # Área logada
    if st.session_state.logged_in:
        st.success(f"Bem-vindo(a), {st.session_state.user_name}!")
        st.subheader("Painel Principal")
        
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Acessar Sistema", type="secondary", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        
        with col2:
            if st.button("Alterar Senha", use_container_width=True):
                st.info("Funcionalidade em desenvolvimento")
        
        with col3:
            if st.button("Sair do Sistema", use_container_width=True):
                # Resetar todos os estados de login
                st.session_state.exit_app = True
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.session_state.show_login = True  # ADICIONADO
                st.session_state.show_signup = False  # ADICIONADO
                st.rerun()

if __name__ == "__main__":
    main()
