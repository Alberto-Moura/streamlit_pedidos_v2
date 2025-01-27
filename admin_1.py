import streamlit as st
import sqlite3
import pandas as pd
from streamlit_app import FRANQUIAS

st.write(f"Você está logado como {st.session_state.role}.")

# Função para consultar o banco de dados
def consultar_pedidos():
    # Conectando ao banco de dados
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    
    # Consulta SQL para buscar todos os registros
    query = """
    SELECT
        codigo_franqueado AS Franqueado,
        condicao_pagamento AS "Condição de Pagamento",
        data_faturamento AS "Data de Faturamento",
        numero_entrada AS "Entrada",
        codigo_produto AS "Código do Produto",
        tamanho_cor AS "Tamanho e Cor",
        quantidade AS "Quantidade",
        valor_total AS "Valor Total (R$)"
    FROM pedidos;
    """
    # Lê o resultado em um DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def qtd_pedidos():
    conn = sqlite3.connect("pedidos.db")
    query = """
    SELECT COUNT(DISTINCT codigo_franqueado) AS total_franqueados
    FROM pedidos;
    """
    cursor = conn.execute(query)
    total_franqueados = cursor.fetchone()[0]
    conn.close()
    return total_franqueados

def consultar_quantidade_total_pecas():
    conn = sqlite3.connect("pedidos.db")
    query = "SELECT SUM(quantidade) AS total_pecas FROM pedidos;"
    cursor = conn.execute(query)
    total_pecas = cursor.fetchone()[0] or 0
    conn.close()
    return total_pecas

def consultar_valor_total_comprado():
    conn = sqlite3.connect("pedidos.db")
    query = "SELECT SUM(valor_total) AS valor_total FROM pedidos;"
    cursor = conn.execute(query)
    valor_total = cursor.fetchone()[0] or 0.0
    conn.close()
    return valor_total

# Função para buscar dados do banco
def get_order_summary_from_db():
    # Conectar ao banco de dados
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()

    # Consulta para agrupar os dados por 'numero_entrada'
    cursor.execute('''
        SELECT numero_entrada, SUM(quantidade) AS quantidade_total, SUM(valor_total) AS valor_total_total
        FROM pedidos
        GROUP BY numero_entrada
    ''')
    summary = cursor.fetchall()

    # Consulta para pegar a 'entry_date' de cada 'numero_entrada'
    cursor.execute('SELECT DISTINCT numero_entrada, data_faturamento FROM pedidos')
    entry_dates = cursor.fetchall()
    entry_date_dict = {entry[0]: entry[1] for entry in entry_dates}

    # Fechar a conexão
    conn.close()

    # Converter o resumo para um DataFrame
    summary_df = pd.DataFrame(summary, columns=["numero_entrada", "quantidade_total", "valor_total_total"])

    # Adicionar a coluna 'Data de Faturamento' usando o 'entry_date_dict'
    summary_df["Data de Faturamento"] = summary_df["numero_entrada"].map(entry_date_dict).fillna("N/A")
    
    return summary_df

# Streamlit para exibir os dados
st.subheader("Consulta de Pedidos", divider=True)

# Consulta os pedidos
df_pedidos = consultar_pedidos()
quantidade_pedidos = qtd_pedidos()
total_pecas = consultar_quantidade_total_pecas()
valor_total_comprado = consultar_valor_total_comprado()
summary_by_entry = get_order_summary_from_db()

# Exibe os cards
col1, col2, col3 = st.columns(3)

with col1:
    #t.subheader("Pedidos Emitidos")
    st.metric(
        label="Franqueados com pedidos",
        value=f"{quantidade_pedidos}/{len(FRANQUIAS) - 1}"
    )

with col2:
    #st.subheader("Peças Compradas")
    st.metric(
        label="Quantidade total de peças",
        value=total_pecas
    )

with col3:
    #st.subheader("Valor Total")
    st.metric(
        label="Valor total comprado",
        value=f"R$ {valor_total_comprado:,.2f}"
    )

# Verifica se há pedidos no banco
if df_pedidos.empty:
    st.warning("Nenhum pedido registrado no momento.")
else:
    # Exibir a tabela
    st.subheader("Resumo por entrada", divider=True)
    st.dataframe(summary_by_entry, use_container_width=True)
    st.subheader("Detalhamento dos Pedidos", divider=True)
    st.dataframe(df_pedidos, use_container_width=True)
    if st.button("Exportar Pedidos"):
        csv_file = f"pedidos_franqueados.csv"
        df_pedidos.to_csv(csv_file, index=False, sep=";", encoding="utf-8-sig")
        st.success(f"Arquivo CSV '{csv_file}' gerado com sucesso!")

        with open(csv_file, "rb") as file:
            st.download_button(
                label="Baixar CSV",
                data=file,
                file_name=csv_file,
                mime="text/csv"
            )
