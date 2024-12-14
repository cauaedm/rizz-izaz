import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
from etl import *
from datetime import datetime

# Título da página
st.title("Dashboard de Tweets")

# Pré-processamento
df = preprocess('tweets.csv')

# Sidebar
with st.sidebar:
    st.title('CCtech salva Rizz-Izaz')
    
    singers_lista = ["Duda Beat", "Kanye West", "Reginald Rossi"]

    selected_singer = st.selectbox('Selecione o cliente', singers_lista)
    df_selected_year = df[df.singer == selected_singer]

    # Garantir que os valores estão no formato correto
    data_min = df['date'].min().to_pydatetime()  # Converte para datetime.datetime
    data_max = df['date'].max().to_pydatetime()  # Converte para datetime.datetime

    # Calcula a data de 1 semana atrás no formato correto
    last_week = data_max - pd.Timedelta(weeks=1)

    # Slider no Streamlit
    data_filter = st.slider(
        "Escolha o preço máximo", 
        min_value=data_min, 
        max_value=data_max, 
        value=last_week
    )

    # Filtrando o DataFrame
    df = df[df['date'] >= pd.to_datetime(data_filter)]

# Layout de colunas
col1, col2 = st.columns(2)


st.title('Dados')
st.dataframe(df)

# Combine todos os tweets em uma única string
text = " ".join(str(tweet) for tweet in df['text'] if isinstance(tweet, str))

# Crie a nuvem de palavras
wordcloud = WordCloud(
    width=800, 
    height=400, 
    background_color='white', 
    colormap='viridis'
).generate(text)

# Converter a nuvem de palavras em imagem
fig = px.imshow(wordcloud, template="plotly_white")
fig.update_layout(
    coloraxis_showscale=False,  # Remove escala de cores desnecessária
    xaxis_visible=False,       # Remove o eixo X
    yaxis_visible=False        # Remove o eixo Y
)

# Exibir a nuvem de palavras no Streamlit
st.plotly_chart(fig)
