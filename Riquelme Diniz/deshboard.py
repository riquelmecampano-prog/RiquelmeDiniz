import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Análise de Comportamento do Consumidor", layout="wide")

# 2. Definição de Cores e Traduções
COR_FUNDO = "#0B1120"
COR_TEXTO = "#D1D5DB"

# Cores coerentes com as estações (Inverno=Azul, Primavera=Verde, Verão=Amarelo, Outono=Laranja)
PALETA_ESTACOES = {
    "Inverno": "#1E3A8A",   
    "Primavera": "#10B981", 
    "Verão": "#F59E0B",     
    "Outono": "#B45309"      
}

# Paleta original colorida para métodos de pagamento
PALETA_PAGAMENTOS = {
    "Cartão de Crédito": "#3B82F6", "Venmo": "#8B5CF6", "Dinheiro": "#10B981",
    "PayPal": "#F59E0B", "Cartão de Débito": "#6366F1", "Transferência": "#EC4899"
}

MAPA_CATEGORIAS = {
    "Clothing": "Vestuário", "Footwear": "Calçados",
    "Outerwear": "Roupas de Sair", "Accessories": "Acessórios"
}

MAPA_GENERO = {"Male": "Masculino", "Female": "Feminino"}

MAPA_PAGAMENTOS = {
    "Credit Card": "Cartão de Crédito", "Debit Card": "Cartão de Débito",
    "Cash": "Dinheiro", "PayPal": "PayPal", "Venmo": "Venmo", "Bank Transfer": "Transferência"
}

# 3. Estilo CSS
st.markdown(f"""
    <style>
    .main {{ background-color: {COR_FUNDO}; }}
    h1, h2, h3, p, span, label {{ color: {COR_TEXTO} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. Carregar e Traduzir Dados
df = pd.read_csv(r"C:\Users\rique\OneDrive\Documentos\Riquelme Diniz\shopping_trends.csv")

# Aplicando traduções
MAPA_TEMPORADAS_ORIGINAL = {"Winter": "Inverno", "Spring": "Primavera", "Summer": "Verão", "Fall": "Outono"}
df['Season'] = df['Season'].map(MAPA_TEMPORADAS_ORIGINAL)
df['Category'] = df['Category'].map(MAPA_CATEGORIAS)
df['Gender'] = df['Gender'].map(MAPA_GENERO)
df['Payment Method'] = df['Payment Method'].map(MAPA_PAGAMENTOS)

# 5. Título e Sidebar com Filtros (Incluindo o filtro específico)
st.title("📊 Dashboard | Análise do Comportamento do Consumidor")
st.markdown("---")

st.sidebar.header("Filtros de Pesquisa")
generos = st.sidebar.multiselect("Gênero:", options=df['Gender'].unique(), default=df['Gender'].unique())
categorias = st.sidebar.multiselect("Categorias:", options=df['Category'].unique(), default=df['Category'].unique())
produtos = st.sidebar.multiselect("Produtos Específicos:", options=df['Item Purchased'].unique(), default=None)

# Aplicar Filtros
df_selection = df.query("Gender in @generos & Category in @categorias")
if produtos:
    df_selection = df_selection.query("`Item Purchased` in @produtos")

# 6. KPIs
total_faturamento = df_selection['Purchase Amount (USD)'].sum()
ticket_medio = df_selection['Purchase Amount (USD)'].mean()
total_vendas = df_selection.shape[0]

k1, k2, k3 = st.columns(3)
k1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k3.metric("Volume de Pedidos", f"{total_vendas:,}".replace(",", "."))

st.markdown("---")

# 7. Layout de Gráficos
col1, col2 = st.columns(2)

with col1:
    # --- Gráfico 1: Estações (Cores Relacionadas) ---
    df_estacao = df_selection.groupby('Season')['Purchase Amount (USD)'].sum().reset_index()
    fig_estacao = px.bar(df_estacao, x='Season', y='Purchase Amount (USD)',
                         color='Season', color_discrete_map=PALETA_ESTACOES,
                         title="Faturamento por Estação",
                         labels={'Season': 'Estação', 'Purchase Amount (USD)': 'Faturamento (R$)'},
                         template="plotly_dark")
    st.plotly_chart(fig_estacao, use_container_width=True)

    # --- Gráfico 2: Pagamentos (Voltado para o visual colorido original) ---
    df_pag = df_selection.groupby('Payment Method').size().reset_index(name='Qtd').sort_values('Qtd', ascending=True)
    fig_pag = px.bar(df_pag, x='Qtd', y='Payment Method', orientation='h',
                     title="Métodos de Pagamento Mais Utilizados",
                     labels={'Payment Method': 'Método', 'Qtd': 'Quantidade'},
                     color='Payment Method', color_discrete_map=PALETA_PAGAMENTOS,
                     template="plotly_dark")
    fig_pag.update_layout(showlegend=False)
    st.plotly_chart(fig_pag, use_container_width=True)

with col2:
    # --- Gráfico 3: Ticket Médio por Categoria (Escala de Cor Relacionada ao Valor) ---
    df_ticket_cat = df_selection.groupby('Category')['Purchase Amount (USD)'].mean().reset_index(name='Ticket Medio').sort_values('Ticket Medio', ascending=True)
    fig_ticket = px.bar(df_ticket_cat, x='Ticket Medio', y='Category', orientation='h',
                        title="Ticket Médio por Categoria (R$)",
                        labels={'Ticket Medio': 'Valor Médio', 'Category': 'Categoria'},
                        color='Ticket Medio', color_continuous_scale="Viridis",
                        template="plotly_dark")
    st.plotly_chart(fig_ticket, use_container_width=True)

    # --- Gráfico 4: Avaliação vs Gasto ---
    fig_scatter = px.scatter(df_selection, x='Review Rating', y='Purchase Amount (USD)', 
                             color='Category' if not produtos else 'Item Purchased',
                             title="Relação: Avaliação dos Clientes vs Gasto",
                             labels={'Review Rating': 'Nota', 'Purchase Amount (USD)': 'Valor Gasto (R$)', 'Category': 'Categoria', 'Item Purchased': 'Produto'},
                             template="plotly_dark", opacity=0.6)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.caption(f"Trabalho de Ciência de Dados para Negócios | Registros filtrados: {total_vendas}")