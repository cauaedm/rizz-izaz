import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
from etl import *
from datetime import datetime
import altair as alt

# Título da página
st.set_page_config(
    page_title="Dashboard",
    page_icon="X",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

preprocessor = Preprocessor('db_config.json')  # Passando o arquivo de configuração JSON

df = preprocessor.extraction()

df = preprocessor.transfrom(df)

# Sidebar
with st.sidebar:
    st.title('CCtech salva Rizz-Izaz')
    
    singers_lista = ["Duda Beat", "Magic Erick", "Reginald Rossi"]
    selected_singer = st.selectbox('Selecione o cliente', singers_lista)
    
    key_words = ["Show", "Álbum", "Música", "EP", "Lançamento", "PodCast", "Polêmica"]
    topics = st.multiselect('Selecione os temas', key_words)
    
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
        "A partir de qual dia", 
        min_value=data_min, 
        max_value=data_max, 
        value=last_week
    )

    # Filtrando o DataFrame
    df = df[df['data_criacao'] >= pd.to_datetime(data_filter)]

    if st.button("Atualizar Dados"):
        try:
            df = df
        except:
            df = df

# Layout de colunas
col1, col2 = st.columns(2)

st.title('Dados')

st.dataframe(df)


'''
# Ignora isso aqui em baixo

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


def make_donut(input_response, input_text, input_color):
    # Define as cores do gráfico com base na entrada
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    else:
        chart_color = ['#CCCCCC', '#888888']  # Cor padrão caso nenhuma seja definida
    
    # DataFrame para os dados do gráfico
    source = pd.DataFrame({
        "Topic": ['', input_text],  # Nome do segmento
        "% value": [100 - input_response, input_response]  # Valores para o gráfico
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]  # Fundo completo do gráfico
    })
    
    # Gráfico principal (segmento filtrado)
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",  # Proporção do gráfico
        color=alt.Color(
            "Topic:N",
            scale=alt.Scale(
                domain=[input_text, ''],
                range=chart_color
            ),
            legend=None
        ),
    ).properties(width=130, height=130)
    
    # Adiciona o texto com a porcentagem
    text = plot.mark_text(
        align='center',
        color=chart_color[0],
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic"
    ).encode(text=alt.value(f'{input_response} %'))
    
    # Gráfico de fundo (para borda e estilo visual)
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color(
            "Topic:N",
            scale=alt.Scale(
                domain=[input_text, ''],
                range=chart_color
            ),
            legend=None
        ),
    ).properties(width=130, height=130)
    
    # Retorna o gráfico combinado
    return plot_bg + plot + text

# Calcular porcentagem dos tweets filtrados
total_tweets = preprocess('tweets.csv').shape[0]  # Total de tweets no arquivo original
filtered_tweets = df.shape[0]  # Total de tweets filtrados
percentage_filtered = round((filtered_tweets / total_tweets) * 100, 2)

# Criar gráfico de donut
donut_chart = make_donut(
    input_response=percentage_filtered, 
    input_text="Tweets Filtrados", 
    input_color="blue"  # Cor do gráfico (pode ajustar)
)

# Exibir o gráfico de donut no Streamlit
st.title("Resumo dos Filtros Aplicados")
st.altair_chart(donut_chart, use_container_width=True)

'''