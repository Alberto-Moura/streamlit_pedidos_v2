import streamlit as st
import sqlite3

# Configuração da Página
#st.set_page_config(page_title="Captação de Pedidos", layout="wide")

ROLES = [None, "Franqueado", "Admin"]
CREDENTIALS = {"admin": "senha123"}
FRANQUIAS = [None, "Franquia A", "Franquia B", "Franquia C"]


def create_database():
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()

    # Criar a tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_franqueado TEXT,
            condicao_pagamento TEXT,
            data_faturamento DATE,
            numero_entrada TEXT,
            codigo_produto TEXT,
            tamanho_cor TEXT,
            quantidade INTEGER,
            valor_total REAL
        )
    ''')

    conn.commit()
    conn.close()

# Criar o banco de dados e a tabela quando o sistema iniciar
create_database()


def login():
    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if role == "Admin":
        password = st.text_input("Password", type="password")
    elif role == "Franqueado":
        # Exibir a lista de franquias para escolha
        franquia = st.selectbox("Escolha sua franquia", FRANQUIAS)
    else:
        password = None  # Não requer senha para outros papéis

    if st.button("Log in"):
        if role == "Admin" and password == CREDENTIALS["admin"]:
            st.session_state.role = role
            st.session_state.franquia = None  # Nenhuma franquia para Admin
            st.rerun()
        elif role == "Franqueado" and franquia != None:
            st.session_state.role = role
            st.session_state.franquia = franquia  # Salvar franquia na sessão
            st.rerun()
        elif role is None:
            st.error("Please select a role")
        else:
            st.error("Invalid credentials")


def logout():
    st.session_state.role = None
    st.rerun()


# Inicializar `st.session_state` se necessário
if "role" not in st.session_state:
    st.session_state.role = None
if "franquia" not in st.session_state:
    st.session_state.franquia = None

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

# Páginas dos franqueados
digitacao_pedido = st.Page(
    "franqueado/digitacao_pedido.py",
    title="Digitação de Pedidos",
    icon=":material/edit:",
    default=(role == "Franqueado"),
)
conferencia_pedido = st.Page(
    "franqueado/conferencia_pedido.py", title="Conferência", icon=":material/check:"
)

# Página do administrador
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")

account_pages = [logout_page, settings]
franquado_pages = [digitacao_pedido, conferencia_pedido]
admin_pages = [admin_1, admin_2]

st.title("Captação de Pedidos")
#st.logo("images/lupo.png", icon_image="images/lupo.png")

page_dict = {}
if st.session_state.role in ["Franqueado", "Admin"]:
    page_dict["Franqueado"] = franquado_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()