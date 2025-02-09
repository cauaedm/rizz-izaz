import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
from sentiment import *
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Visual",
    page_icon="X",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema do Altair
default_theme = alt.themes.enable("default")
# Gerando datas com repetição (algumas datas se repetem)
datas = pd.date_range(start="2023-01-01", periods=100, freq="D")
datas_repetidas = np.random.choice(datas, size=120, replace=True)  # 120 datas com repetição

# Gerando o sentimento desbalanceado
df = pd.read_csv(r'C:\Users\otpok\UFRJ CC\rizz-izaz\dataset_easy-twitter-search-scraper_2025-02-06_22-54-21-377.csv')
df['sentimento'] = 0
# Sidebar
with st.sidebar:
    st.title('CCtech <> Rizz-Izaz')
    singers_lista = ["Duda Beat", "Magic Eric", "Deadcat", "Orlas"]
    selected_singer = st.selectbox('Selecione o cliente', singers_lista)
    
    key_words = ["show", "album", "musica", "lancamento", "treta"]
    topics = st.multiselect('Selecione os temas', key_words, max_selections=2)

    if st.button("Atualizar dados"):
        df = pd.read_csv(r'C:\Users\otpok\UFRJ CC\rizz-izaz\dataset_easy-twitter-search-scraper_2025-02-06_22-54-21-377.csv')
        sentiment = Sentiment()
        with st.spinner("Analisando tweets..."):
            df = sentiment.analyse(df)

        # Após o carregamento, exibe uma nova mensagem
        st.success('Tweets atualizados!')

        df.to_csv('dados_antigos.csv', index=False)

col = st.columns((1.5, 4.5, 2), gap='medium')

positivos = df[df['sentimento']== 1].shape[0]
negativos = df[df['sentimento']== -1].shape[0]


# Métricas gerais//////////////
with col[0]:
    st.markdown('### Métricas')
    st.metric(
        label="Quantidade de positivos", 
        value=positivos
    )
    st.metric(
        label="Qtde de tweets negativos", 
        value=negativos
    )

    # Verificando se a soma dos positivos e negativos é diferente de zero
    if (positivos + negativos) != 0:
        taxa = positivos / (positivos + negativos)
    else:
        taxa = 0  # Ou qualquer outro valor padrão que você queira atribuir

    # Exibindo o resultado
    st.metric(
        label="Proporção Positiva",
        value=f"{taxa:.2f}"  # Exibe a proporção com duas casas decimais
    )

    st.metric(
        label="Curtidas associadas",
        value=locale.format_string("%d", df['likes'].sum(), grouping=True)
    )
    st.metric(
        label="Retweets associados",
        value=locale.format_string("%d", df['retweets'].sum(), grouping=True)
    )
    st.metric(
        label="Quantidade de verificados",
        value=locale.format_string("%d", df['verified'].sum(), grouping=True)
    )

# Exibição de tabela
with col[1]:
    st.markdown('### Dados')

    colunas = st.multiselect(
        "Escolha as colunas para exibir:", 
        options=['text', 'likes', 'retweets', 'fullname', 'sentimento'],
        default=['fullname', 'text'] # Seleciona as 3 primeiras colunas por padrão
    )

    # Exibição da tabela com as colunas selecionadas
    st.markdown("### Amostra de Dados")
    if colunas:
        st.dataframe(df[colunas].head(), use_container_width=True, hide_index=True)
    else:
        st.markdown("**Nenhuma coluna selecionada. Por favor, escolha ao menos uma coluna na barra lateral.**")

    # Botão para download
    st.download_button(
        label="Baixar Completo como Excel",
        data="Simulação de dados para download.",
        file_name="tweets_simulados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# Gráfico de linha com Plotly
with col[2]:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    sentiment_counts = df.groupby([df['timestamp'].dt.date, 'sentimento']).size().reset_index(name='Contagem')
    fig = px.line(
        sentiment_counts,
        x='timestamp',
        y='Contagem',
        color='sentimento',
        labels={'Sentimento': 'Sentimento', 'Contagem': 'Contagem de Tweets', 'Data de Criação': 'Data'},
        title="Sentimento ao longo do tempo"
    )
    fig.update_layout(
        template='plotly_dark',
        title={'font': {'color': 'white'}},
        xaxis_title={'font': {'color': 'white'}},
        yaxis_title={'font': {'color': 'white'}},
        font={'color': 'white'},
        height=300
    )
    st.plotly_chart(fig)
