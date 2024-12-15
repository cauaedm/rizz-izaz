import pymysql
import json
import pandas as pd

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
        
    
    def transfrom(self, df):
        df['singer'] = 'Duda Beat'

        return df