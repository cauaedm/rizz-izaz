import pymysql
import json
import pandas as pd
import re

class Preprocessor:
    def __init__(self, config_file):
        try:
            # Ler as configurações do arquivo JSON
            with open(config_file, 'r') as file:
                db_config = json.load(file)
            
            # Conectar ao banco de dados
            self.conn = pymysql.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                port=db_config['port'],
                database=db_config['database']
            )

            print("Conexão bem-sucedida!")

            # Criar um cursor para executar comandos SQL
            self.cursor = self.conn.cursor()

        except pymysql.MySQLError as e:
            print("Erro ao conectar ao MySQL:", e)

    def extraction(self):
        select_query = "SELECT * FROM tweets"

        # Carregar os dados em um DataFrame do pandas
        df = pd.read_sql(select_query, self.conn)
        return df

    def load(self, df):
        def preencher_valores(df):
            for column in df.columns:
                if df[column].dtype in ['int64', 'float64']:  # Para colunas numéricas
                    df[column] = df[column].fillna(0)
                elif df[column].dtype == 'object':  # Para colunas de texto
                    df[column] = df[column].fillna('')
            return df

        # Preencher valores nulos
        df = preencher_valores(df)

        # Converter DataFrame para lista de listas
        dados = df.values.tolist()

        # Query de inserção
        insert_query = """
        INSERT INTO tweets (
            id_usuario, nome_usuario, nome_completo, data_criacao,
            numero_curtidas, numero_retweets, numero_respostas, texto_tweet,
            idioma, localizacao, id_conversa, fonte, tweets_referenciados, anexos
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Executar o comando de inserção para cada linha
        try:
            self.cursor.executemany(insert_query, dados)
            self.conn.commit()
            print("Dados inseridos com sucesso!")
        except Exception as e:
            print("Erro ao inserir os dados:", e)
            self.conn.rollback()
        
    def transform(self, df, text_column="texto_tweet"):
        # Função interna para limpar o texto
        def clean_text(text):
            text = re.sub(r"@\w+", "", text)  # Remove menções
            text = re.sub(r"http\S+|www\S+", "", text)  # Remove URLs
            text = re.sub(r"#\w+", "", text)  # Remove hashtags
            text = re.sub(r"[^\w\s]", "", text)  # Remove pontuações
            text = text.lower().strip()  # Converte para minúsculas e remove espaços extras
            return text  # Retorna o texto limpo
        
        # Aplica a função de limpeza na coluna especificada
        df[text_column] = df[text_column].apply(lambda x: clean_text(x))  # Certifique-se de passar o texto para a função
        return df
    
    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexão fechada.")