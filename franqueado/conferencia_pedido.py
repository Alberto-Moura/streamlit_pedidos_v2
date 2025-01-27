import streamlit as st
import pandas as pd
import sqlite3
from time import sleep

products = [
    {"code": "P001", "name": "Camiseta", "sizes": ["P", "M", "G"], "colors": ["Vermelho", "Azul"], "price": 50.0, "image": "https://luposport.vtexassets.com/arquivos/ids/225845-1200-auto?v=638621663186470000&width=1200&height=auto&aspect=true", "entry": "Entrada 1", "grade": {"P": 10, "M": 15, "G": 20}, "entry_date": "2025-02-01"},
    {"code": "P002", "name": "Calça", "sizes": ["38", "40", "42"], "colors": ["Preto", "Bege"], "price": 100.0, "image": "https://luposport.vtexassets.com/arquivos/ids/234606-1200-auto?v=638732387207030000&width=1200&height=auto&aspect=true", "entry": "Entrada 2", "grade": {"38": 5, "40": 10, "42": 15}, "entry_date": "2025-02-10"},
    {"code": "P003", "name": "Jaqueta", "sizes": ["M", "G"], "colors": ["Preto", "Azul"], "price": 200.0, "image": "https://luposport.vtexassets.com/arquivos/ids/230553-1200-auto?v=638621663905900000&width=1200&height=auto&aspect=true", "entry": "Entrada 3", "grade": {"M": 8, "G": 12}, "entry_date": "2025-02-20"}
]

# Função para salvar os pedidos no banco de dados
def save_order_to_db(order):
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pedidos (codigo_franqueado, condicao_pagamento, data_faturamento, 
                             numero_entrada, codigo_produto, tamanho_cor, quantidade, valor_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order['codigo_franqueado'],
        order['condicao_pagamento'],
        order['data_faturamento'],
        order['numero_entrada'],
        order['codigo_produto'],
        order['tamanho_cor'],
        order['quantidade'],
        order['valor_total']
    ))

    conn.commit()
    conn.close()

# Função para revisar e finalizar o pedido
def review_page():

    if st.session_state.orders:
        st.subheader("Resumo do Pedido", divider=True)
        
        df_orders = pd.DataFrame(st.session_state.orders)

        st.write(f"Franqueado: **{st.session_state.franquia}**")
        st.write(f"Condição de Pagamento: **{df_orders.iloc[0]['condicao_pagamento']}**")

        total_pieces = df_orders["quantidade"].sum()
        total_value = df_orders["valor_total"].sum()

        cols = st.columns(2)
        with cols[0]:
            st.metric(label="Total de Peças", value=total_pieces)
        with cols[1]:
            st.metric(label="Valor Total (R$)", value=f"{total_value:.2f}")

        # Resumo por entrada
        st.subheader("Resumo por Entrada", divider=True)
        summary_by_entry = df_orders.groupby("numero_entrada")[["quantidade", "valor_total"]].sum()
        summary_by_entry["Data de Faturamento"] = summary_by_entry.index.map(
            lambda x: next((p["entry_date"] for p in products if p["entry"] == x), "N/A")
        )
        st.dataframe(summary_by_entry, use_container_width=True)

         # Exibição da tabela detalhada
        st.subheader("Detalhamento do Pedido", divider=True)
        display_df = df_orders.drop(columns=["codigo_franqueado", "condicao_pagamento", "data_faturamento"])
        display_df.reset_index(drop=True, inplace=True)
        st.dataframe(display_df, use_container_width=True)

        # Botões separados
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Voltar e Corrigir"):
                for order in st.session_state.orders:
                    qty_key = f"qty_{order['codigo_produto']}_{order['tamanho_cor'].replace(' - ', '_')}"
                    st.session_state[qty_key] = order["quantidade"]
                st.session_state.orders = []
                st.switch_page("franqueado/digitacao_pedido.py")

        with col2:
            if st.button("Finalizar Pedido"):
                for order in st.session_state.orders:
                    save_order_to_db(order)
                st.session_state.orders = []
                st.success("Pedido finalizado com sucesso!")
                sleep(2)
                st.rerun()

        with col3:
            if st.button("Finalizar Pedido e Gerar CSV"):
                csv_file = f"pedido_franqueado_{st.session_state.franquia}.csv"
                df_orders.to_csv(csv_file, index=False, sep=";", encoding="utf-8-sig")
                st.success(f"Arquivo CSV '{csv_file}' gerado com sucesso!")
    
                with open(csv_file, "rb") as file:
                    st.download_button(
                        label="Baixar CSV",
                        data=file,
                        file_name=csv_file,
                        mime="text/csv"
                    )

st.subheader("Conferência de Pedidos")

# Chama a função de conferência
review_page()
