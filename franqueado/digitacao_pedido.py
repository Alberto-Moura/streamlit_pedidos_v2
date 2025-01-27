import streamlit as st
import pandas as pd
from datetime import date

# Dados de produtos (aqui está a listagem de produtos com preços, tamanhos, etc)
products = [
    {"code": "P001", "name": "Camiseta", "sizes": ["P", "M", "G"], "colors": ["Vermelho", "Azul"], "price": 50.0, "image": "https://luposport.vtexassets.com/arquivos/ids/225845-1200-auto?v=638621663186470000&width=1200&height=auto&aspect=true", "entry": "Entrada 1", "grade": {"P": 2, "M": 3, "G": 2}, "entry_date": "2025-02-01"},
    {"code": "P002", "name": "Calça", "sizes": ["38", "40", "42"], "colors": ["Preto", "Bege"], "price": 100.0, "image": "https://luposport.vtexassets.com/arquivos/ids/234606-1200-auto?v=638732387207030000&width=1200&height=auto&aspect=true", "entry": "Entrada 2", "grade": {"38": 1, "40": 2, "42": 2}, "entry_date": "2025-02-10"},
    {"code": "P003", "name": "Jaqueta", "sizes": ["M", "G"], "colors": ["Preto", "Azul"], "price": 200.0, "image": "https://luposport.vtexassets.com/arquivos/ids/230553-1200-auto?v=638621663905900000&width=1200&height=auto&aspect=true", "entry": "Entrada 3", "grade": {"M": 2, "G": 2}, "entry_date": "2025-02-20"}
]

# Criando um DataFrame para manipular os dados
product_variants = []
for product in products:
    for size in product["sizes"]:
        for color in product["colors"]:
            product_variants.append({
                "Imagem": product["image"],
                "Produto": product["name"],
                "Código": product["code"],
                "Tamanho": size,
                "Cor": color,
                "Preço": product["price"],
                "Entrada": product["entry"],
                "Grade": product["grade"][size],
                "Data de Entrada": product["entry_date"],
                "Quantidade": 0
            })

product_df = pd.DataFrame(product_variants)
product_df.sort_values(by=["Código", "Cor"], inplace=True)

payment_conditions = ["Selecione uma condição", "C002 - 14 Dias (10% + 5% + 6%)", "30 dias", "60 dias", "90 dias"]

# Captura do pedido
def main_page():
    
    st.subheader("Digitação de Pedidos - Franqueados", divider=True)
    st.write(f"Você está logado no franqueado: **{st.session_state.franquia}**.")

    payment_condition = st.selectbox("Condição de Pagamento", payment_conditions)

    # Se não houver pedidos, inicializa
    if "orders" not in st.session_state:
        st.session_state.orders = []

    st.subheader("Seleção de Produtos", divider=True)

    if "orders" not in st.session_state:
        st.session_state.orders = []

    # Construção da tabela de produtos
    quantities = []
    for _, row in product_df.iterrows():
        cols = st.columns([2, 2, 1, 1, 2, 2, 3, 2])
        with cols[0]:
            st.image(row["Imagem"], width=75)
        with cols[1]:
            st.text(row["Produto"])
        with cols[2]:
            st.text(row["Código"])
        with cols[3]:
            st.text(row["Tamanho"])
        with cols[4]:
            st.text(row["Cor"])
        with cols[5]:
            st.text(row["Entrada"])
        with cols[6]:
            st.text(f'Grade sugerida: {row["Grade"]}')
        with cols[7]:
            qty_key = f"qty_{row['Código']}_{row['Tamanho']}_{row['Cor']}"
            quantity = st.number_input(
                "Quantidade",
                min_value=0,
                value=st.session_state.get(qty_key, 0),
                key=qty_key
            )
            quantities.append(quantity)

    product_df["Quantidade"] = quantities

    # Quando o usuário clica em "Adicionar ao Pedido"
    if st.button("Adicionar ao Pedido e Conferir"):

        # Verifica se a condição de pagamento foi selecionada
        if payment_condition == "Selecione uma condição":
            st.error("Por favor, selecione uma condição de pagamento antes de prosseguir.")
            return

        # Verifica se todas as quantidades estão zeradas
        if all(qty == 0 for qty in quantities):
            st.error("Por favor, insira pelo menos uma quantidade válida antes de prosseguir.")
            return

        for _, row in product_df.iterrows():
            if row["Quantidade"] > 0:
                order = {
                    "codigo_franqueado": st.session_state.franquia,  # Exemplo de franquia
                    "condicao_pagamento": payment_condition,  # Condição de pagamento exemplo
                    "data_faturamento": date.today(),
                    "numero_entrada": row["Entrada"],
                    "codigo_produto": row["Código"],
                    "tamanho_cor": f"{row['Tamanho']} - {row['Cor']}",
                    "quantidade": row["Quantidade"],
                    "valor_total": row["Quantidade"] * row["Preço"]
                }
                st.session_state.orders.append(order)
        st.switch_page("franqueado/conferencia_pedido.py")

# Chama a função principal de captura de pedidos
main_page()
