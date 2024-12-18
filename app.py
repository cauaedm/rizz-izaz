import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
from etl import *
from datetime import datetime, timedelta
import altair as alt
from scraper import *
import io

# Título da página
st.set_page_config(
    page_title="Dashboard",
    page_icon="X",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

# Data
preprocessor = Preprocessor('db_config.json')  # Passando o arquivo de configuração JSON
df = preprocessor.extraction()
df = preprocessor.transform(df)
new_data=None
#Scraper
scraper = TwitterAPI('config.ini')

df_with_sentiment = pd.read_csv(r'df_with_sentiment.csv')

# Sidebar
with st.sidebar:
    st.title('CCtech salva Rizz-Izaz')
    
    singers_lista = ["Duda Beat", "Magic Eric", "Deadcat", "Orlas"]
    selected_singer = st.selectbox('Selecione o cliente', singers_lista)
    
    key_words = ["show", "album", "musica", "lancamento", "treta"]
    topics = st.multiselect('Selecione os temas', key_words, max_selections=2)

    df = df[df.singer == selected_singer]
    
    if len(df)<1:
        df=df[df.singer == 'Duda Beat']

    # Garantir que os valores estão no formato correto
    data_min = df['data_criacao'].min().to_pydatetime()  # Converte para datetime.datetime
    data_max = df['data_criacao'].max().to_pydatetime()  # Converte para datetime.datetime

    # Calcula a data de 1 semana atrás no formato correto
    last_week = data_max - pd.Timedelta(weeks=1)

    # Slider no Streamlit
    data_filter = st.slider(
        "Selecione o dia e hora:",
        min_value=data_min,
        max_value=data_max,
        value=last_week,
        format="DD-MM HH:mm",  # Formato que inclui apenas hora e minuto
        step=timedelta(minutes=1)  # Ajuste em incrementos de 1 minuto
    )
    
    df = df[df['data_criacao'] >= data_filter]
    df_with_sentiment['Data de Criação'] = pd.to_datetime(df_with_sentiment['Data de Criação']).dt.tz_localize(None)
    df_with_sentiment = df_with_sentiment[df_with_sentiment['Data de Criação']>= data_filter]
    if st.button("Atualizar Dados"):
        preprocessor = Preprocessor('db_config.json')  # Passando o arquivo de configuração JSON
        new_data = scraper.search_tweets(search_query=selected_singer, topics=topics)
        preprocessor.load(new_data)
        new_df = preprocessor.extraction()
        df = new_df

col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    try:
        # Calculando métricas gerais
        qtde_positivo = len(df_with_sentiment[df_with_sentiment['sentimento'] == 1])
        qtde_negativo = len(df_with_sentiment[df_with_sentiment['sentimento'] == -1])
        positive_rate = qtde_positivo / (qtde_negativo + qtde_positivo)

        # Dividindo os tweets em dois períodos (recentes x antigos)
        recent_tweets = df_with_sentiment[df_with_sentiment['Data de Criação'] >= (data_max - timedelta(days=1))]
        older_tweets = df_with_sentiment[df_with_sentiment['Data de Criação'] < (data_max - timedelta(days=1))]

        # Taxas de positivos nos dois períodos
        recent_positive_rate = len(recent_tweets[recent_tweets['sentimento'] == 1]) / len(recent_tweets)
        older_positive_rate = len(older_tweets[older_tweets['sentimento'] == 1]) / len(older_tweets)

        # Variação na taxa de positivos
        positive_rate_delta = recent_positive_rate - older_positive_rate

        # Exibindo métricas
        st.markdown('### Métricas')
        
        st.metric(
            label="Qtde de tweets positivos", 
            value=qtde_positivo
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.metric(
            label="Qtde de tweets negativos", 
            value=qtde_negativo
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.metric(
            label="Percentual de positivos", 
            value=f"{positive_rate:.2%}", 
            delta=f"{positive_rate_delta:.2%}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
    except:
        # Mensagem de erro estilizada
        with st.container():
            st.markdown(
                """
                <div style="
                    border: 2px solid #FF4B4B; 
                    border-radius: 10px; 
                    padding: 20px; 
                    background-color: #FFEDED;
                    text-align: center;">
                    <h3 style="color: #FF4B4B;">Ops! Algo deu errado</h3>
                    <p style="color: #555;">
                        Nenhum tweet corresponde ao filtro aplicado.<br>
                        Por favor, revise os critérios de busca e tente novamente.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

with col[1]:
    colunas = df.columns
    colunas = st.multiselect('Selecione as Colunas', colunas, max_selections=5)
    # Exibindo a título e dados em uma área mais larga
    st.markdown('### Dados')
    
    # Exibindo o dataframe
    new_df = preprocessor.transform(df)
    st.dataframe(new_df[colunas], use_container_width=True, hide_index=True)  # Faz o dataframe usar toda a largura disponível

    def to_xlsx(df):
        # Cria um buffer de memória
        buffer = io.BytesIO()
        # Converte o DataFrame para um arquivo Excel no buffer
        df.to_excel(buffer, index=False, sheet_name='Tweets')
        buffer.seek(0)
        return buffer

    # Botão de download para o DataFrame em formato Excel
    st.download_button(
        label="Baixar como Excel",
        data=to_xlsx(new_df),
        file_name="tweets.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    # Combine todos os tweets em uma única string
    text = " ".join(str(tweet) for tweet in df['texto_tweet'] if isinstance(tweet, str))

    # Criação da nuvem de palavras
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white', 
        colormap='viridis'
    ).generate(text)

with col[2]:
    # Converter a coluna 'Data de Criação' para datetime
    df_with_sentiment['Data de Criação'] = pd.to_datetime(df['data_criacao'], errors='coerce')

    # Agrupar por data e sentimento
    sentiment_counts = df_with_sentiment.groupby([df['data_criacao'].dt.date, 'sentimento']).size().reset_index(name='count')

    # Criar o gráfico de linha com Plotly
    fig = px.line(
        sentiment_counts, 
        x='data_criacao', 
        y='count', 
        color='sentimento', 
        labels={'sentimento': 'Sentimento', 'count': 'Contagem de Tweets', 'data_criacao': 'Data'},
        title="Sentimento ao longo do tempo"
    )

    # Definir o tema de fundo do gráfico como dark
    fig.update_layout(
        template='plotly_dark',
        title={'font': {'color': 'white'}},  # Título em branco
        xaxis_title={'font': {'color': 'white'}},  # Eixo X em branco
        yaxis_title={'font': {'color': 'white'}},  # Eixo Y em branco
        font={'color': 'white'},  # Texto em branco
        height=300,
        xaxis={'tickangle': 0}  # Define a legenda do eixo X na horizontal (0 graus)
    )

    # Exibindo o gráfico no Streamlit
    with st.container():
        st.plotly_chart(fig)