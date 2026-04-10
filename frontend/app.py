"""Frontend web com Streamlit"""
import os
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

# Configuração da página
st.set_page_config(
    page_title="BancoApp - Sistema Bancário",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        font-size: 3em;
        margin-bottom: 2em;
    }
    .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .balance-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# URL da API
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Estado da sessão
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_account" not in st.session_state:
    st.session_state.current_account = None


def get_headers():
    """Retorna headers com autenticação"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login(email: str, password: str):
    """Autentica usuário"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            # Obtém dados do usuário
            user_response = requests.get(
                f"{API_URL}/users/me",
                headers=get_headers()
            )
            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
                st.success("Login realizado com sucesso!")
                st.rerun()
        else:
            st.error("Email ou senha inválidos")
    except Exception as e:
        st.error(f"Erro ao fazer login: {str(e)}")


def register(email: str, username: str, full_name: str, cpf: str, password: str, birth_date: str):
    """Registra novo usuário"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "email": email,
                "username": username,
                "full_name": full_name,
                "cpf": cpf,
                "password": password,
                "birth_date": f"{birth_date}T00:00:00",
            },
        )
        if response.status_code == 201:
            st.success("Usuário registrado com sucesso! Faça login para continuar.")
        else:
            st.error(response.json().get("detail", "Erro ao registrar"))
    except Exception as e:
        st.error(f"Erro ao registrar: {str(e)}")


def logout():
    """Faz logout do usuário"""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.current_account = None
    st.success("Logout realizado com sucesso!")
    st.rerun()


def main():
    """Função principal da aplicação"""
    
    # Barra lateral
    with st.sidebar:
        st.markdown("# 🏦 BancoApp")
        st.divider()
        
        if st.session_state.user:
            st.markdown(f"**Bem-vindo, {st.session_state.user.get('full_name')}!**")
            st.divider()
            
            option = st.radio(
                "Menu",
                [
                    "Dashboard",
                    "Contas",
                    "Transações",
                    "Perfil",
                    "Sair",
                ]
            )
        else:
            option = st.radio(
                "Menu",
                [
                    "Login",
                    "Registrar",
                ]
            )
    
    # Conteúdo principal
    if not st.session_state.user:
        st.markdown('<div class="main-header">🏦 Sistema Bancário</div>', unsafe_allow_html=True)
        
        if option == "Login":
            st.subheader("Login")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Senha", type="password", key="login_password")
                
                if st.button("Entrar", use_container_width=True):
                    if email and password:
                        login(email, password)
                    else:
                        st.warning("Preencha todos os campos")
        
        elif option == "Registrar":
            st.subheader("Criar Conta")
            with st.form("register_form"):
                email = st.text_input("Email")
                username = st.text_input("Usuário")
                full_name = st.text_input("Nome Completo")
                cpf = st.text_input("CPF")
                birth_date = st.date_input("Data de Nascimento")
                password = st.text_input("Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                
                if st.form_submit_button("Registrar", use_container_width=True):
                    if password == confirm_password:
                        if all([email, username, full_name, cpf, password]):
                            register(email, username, full_name, cpf, password, str(birth_date))
                        else:
                            st.error("Preencha todos os campos")
                    else:
                        st.error("As senhas não coincidem")
    
    else:
        # Menu autenticado
        if option == "Dashboard":
            st.title("Dashboard")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Nome", st.session_state.user.get("full_name", "N/A"))
            with col2:
                st.metric("Email", st.session_state.user.get("email", "N/A"))
            with col3:
                st.metric("Status", "Ativo" if st.session_state.user.get("is_active") else "Inativo")
            
            st.divider()
            st.subheader("Saldo Total")
            
            try:
                response = requests.get(
                    f"{API_URL}/accounts/total-balance",
                    headers=get_headers()
                )
                if response.status_code == 200:
                    data = response.json()
                    st.markdown(f'<div class="balance-card"><h2>R$ {data.get("total_balance", 0):.2f}</h2></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao obter saldo: {str(e)}")
        
        elif option == "Contas":
            st.title("Minhas Contas")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button("+ Nova Conta", use_container_width=True):
                    st.session_state.new_account_form = True
            
            if st.session_state.get("new_account_form"):
                st.subheader("Criar Nova Conta")
                with st.form("new_account"):
                    account_type = st.selectbox("Tipo de Conta", ["corrente", "poupanca", "investimento"])
                    overdraft = st.number_input("Limite de Saque (R$)", value=0.0)
                    
                    if st.form_submit_button("Criar Conta"):
                        try:
                            response = requests.post(
                                f"{API_URL}/accounts/",
                                json={
                                    "account_type": account_type,
                                    "overdraft_limit": overdraft if account_type == "corrente" else 0,
                                },
                                headers=get_headers()
                            )
                            if response.status_code == 201:
                                st.success("Conta criada com sucesso!")
                                st.session_state.new_account_form = False
                                st.rerun()
                            else:
                                st.error(response.json().get("detail", "Erro ao criar conta"))
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")
            
            try:
                response = requests.get(
                    f"{API_URL}/accounts/?skip=0&limit=10",
                    headers=get_headers()
                )
                if response.status_code == 200:
                    data = response.json()
                    if data["items"]:
                        for account in data["items"]:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**{account['account_number']}**")
                            with col2:
                                st.write(f"Saldo: R$ {account['balance']:.2f}")
                            with col3:
                                st.write(f"Tipo: {account['account_type']}")
                    else:
                        st.info("Você não possui contas ainda")
            except Exception as e:
                st.error(f"Erro ao listar contas: {str(e)}")
        
        elif option == "Transações":
            st.title("Transações")
            
            st.subheader("Operações")
            tab1, tab2, tab3 = st.tabs(["Depósito", "Saque", "Transferência"])
            
            try:
                # Obter contas do usuário
                accounts_response = requests.get(
                    f"{API_URL}/accounts/?skip=0&limit=10",
                    headers=get_headers()
                )
                accounts = accounts_response.json()["items"] if accounts_response.status_code == 200 else []
                account_options = {f"{a['account_number']} - {a['account_type']}": a['id'] for a in accounts}
                
                with tab1:
                    st.subheader("Depósito")
                    if account_options:
                        with st.form("deposit_form"):
                            account_select = st.selectbox("Selecione a conta", list(account_options.keys()), key="deposit_account")
                            amount = st.number_input("Valor (R$)", value=0.0, min_value=0.01, key="deposit_amount")
                            description = st.text_input("Descrição", key="deposit_desc")
                            
                            if st.form_submit_button("Depositar"):
                                response = requests.post(
                                    f"{API_URL}/transactions/deposit?account_id={account_options[account_select]}&amount={amount}&description={description}",
                                    headers=get_headers()
                                )
                                if response.status_code == 201:
                                    st.success("Depósito realizado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(response.json().get("detail"))
                    else:
                        st.warning("Você não possui contas")
                
                with tab2:
                    st.subheader("Saque")
                    if account_options:
                        with st.form("withdrawal_form"):
                            account_select = st.selectbox("Selecione a conta", list(account_options.keys()), key="withdrawal_account")
                            amount = st.number_input("Valor (R$)", value=0.0, min_value=0.01, key="withdrawal_amount")
                            description = st.text_input("Descrição", key="withdrawal_desc")
                            
                            if st.form_submit_button("Sacar"):
                                response = requests.post(
                                    f"{API_URL}/transactions/withdrawal?account_id={account_options[account_select]}&amount={amount}&description={description}",
                                    headers=get_headers()
                                )
                                if response.status_code == 201:
                                    st.success("Saque realizado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(response.json().get("detail"))
                    else:
                        st.warning("Você não possui contas")
                
                with tab3:
                    st.subheader("Transferência")
                    if account_options:
                        with st.form("transfer_form"):
                            account_select = st.selectbox("De qual conta", list(account_options.keys()), key="transfer_account")
                            target_account = st.text_input("Conta destino")
                            amount = st.number_input("Valor (R$)", value=0.0, min_value=0.01, key="transfer_amount")
                            description = st.text_input("Descrição", key="transfer_desc")
                            
                            if st.form_submit_button("Transferir"):
                                if target_account:
                                    response = requests.post(
                                        f"{API_URL}/transactions/transfer?source_account_id={account_options[account_select]}",
                                        json={
                                            "target_account_number": target_account,
                                            "amount": amount,
                                            "description": description,
                                        },
                                        headers=get_headers()
                                    )
                                    if response.status_code == 201:
                                        st.success("Transferência realizada com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(response.json().get("detail"))
                                else:
                                    st.error("Informe a conta de destino")
                    else:
                        st.warning("Você não possui contas")
            
            except Exception as e:
                st.error(f"Erro: {str(e)}")
        
        elif option == "Perfil":
            st.title("Meu Perfil")
            
            with st.form("profile_form"):
                st.text_input("Email", st.session_state.user["email"], disabled=True)
                full_name = st.text_input("Nome Completo", st.session_state.user["full_name"])
                phone = st.text_input("Telefone", st.session_state.user.get("phone", ""))
                
                if st.form_submit_button("Atualizar Perfil"):
                    response = requests.put(
                        f"{API_URL}/users/me",
                        json={
                            "full_name": full_name,
                            "phone": phone,
                        },
                        headers=get_headers()
                    )
                    if response.status_code == 200:
                        st.session_state.user = response.json()
                        st.success("Perfil atualizado com sucesso!")
                    else:
                        st.error("Erro ao atualizar perfil")
            
            st.divider()
            st.subheader("Segurança")
            with st.form("password_form"):
                old_password = st.text_input("Senha Atual", type="password")
                new_password = st.text_input("Nova Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                
                if st.form_submit_button("Alterar Senha"):
                    if new_password == confirm_password:
                        try:
                            response = requests.post(
                                f"{API_URL}/users/change-password?old_password={old_password}&new_password={new_password}",
                                headers=get_headers()
                            )
                            if response.status_code == 200:
                                st.success("Senha alterada com sucesso!")
                            else:
                                st.error("Erro ao alterar senha")
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")
                    else:
                        st.error("As senhas não coincidem")
        
        elif option == "Sair":
            logout()


if __name__ == "__main__":
    main()
