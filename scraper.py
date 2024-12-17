import time
import tweepy
import pandas as pd
import configparser

class TwitterAPI:
    def __init__(self, config_file='config.ini'):
        """
        Inicializa a classe com o arquivo de configuração que contém o Bearer Token.
        """
        self.bearer_token = self._load_config(config_file)
        self.client = tweepy.Client(bearer_token=self.bearer_token)

    def _load_config(self, config_file):
        """
        Carrega a chave Bearer Token a partir de um arquivo INI.
        """
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
            return config['TwitterAPI']['bearer_token']
        except FileNotFoundError:
            print(f"Arquivo {config_file} não encontrado.")
            raise
        except KeyError:
            print("Bearer Token não encontrado no arquivo de configuração.")
            raise

    def generate_query(self, search_query, topics):
        """
        Gera a query de pesquisa com base no tópico e sinônimos.
        """
        show_synonyms = [
            "apresentação", 
            "espetáculo", 
            "performance", 
            "exibição", 
            "evento", 
            "concerto", 
            "palestra", 
            "representação", 
            "evento ao vivo", 
            "exibição ao vivo"
        ]

        music_synonyms = [
            "canção", 
            "melodia", 
            "faixa", 
            "composição", 
            "tema", 
            "som", 
            "hino", 
            "música clássica", 
            "obra", 
            "partitura"
        ]

        album_synonyms = [
            "disco", 
            "LP", 
            "compilado", 
            "gravação", 
            "obra", 
            "trabalho", 
            "coleção", 
            "conjunto de músicas", 
            "cd", 
            "vídeo musical"
        ]

        treta_synonyms = [
            "confusão", 
            "briga", 
            "disputa", 
            "conflito", 
            "rivalidade", 
            "altercação", 
            "desentendimento", 
            "desavença", 
            "barraco", 
            "encrenca"
        ]

        launch_synonyms = [
            "estreia", 
            "lançamento", 
            "divulgação", 
            "início", 
            "inauguração", 
            "apresentação", 
            "introdução", 
            "debut", 
            "revelação", 
            "publicação"
        ]

        # Construir a parte da query com base no tópico
        search_query = search_query + ' AND ('
        for topic in topics:
            if topic == 'show':
                query = ''
                for key_word in show_synonyms:
                    if query:
                        query += ' OR '  # Adiciona "OR" entre os sinônimos
                    query += f'"{key_word}"'
                search_query += query

            elif topic == 'musica':
                query = ''
                for key_word in music_synonyms:
                    if query:
                        query += ' OR '
                    query += f'"{key_word}"'
                search_query += query

            elif topic == 'album':
                query = ''
                for key_word in album_synonyms:
                    if query:
                        query += ' OR '
                    query += f'"{key_word}"'
                search_query += query

            elif topic == 'treta':
                query = ''
                for key_word in treta_synonyms:
                    if query:
                        query += ' OR '
                    query += f'"{key_word}"'
                search_query += query

            elif topic == 'lancamento':
                query = ''
                for key_word in launch_synonyms:
                    if query:
                        query += ' OR '
                    query += f'"{key_word}"'
                search_query += query

            search_query += ')'
    
        return search_query

    def search_tweets(self, search_query, no_of_tweets=10, topics=None):
        if topics:
            complete_query = self.generate_query(search_query, topics)
        else:
            complete_query = search_query

        try:
            response = self.client.search_recent_tweets(
                query=complete_query,
                max_results=no_of_tweets,
                tweet_fields=[ 'created_at', 'public_metrics', 'author_id', 'geo', 'entities',
                               'context_annotations', 'lang', 'conversation_id', 'referenced_tweets', 
                               'source', 'attachments' ],
                user_fields=['name', 'username', 'location', 'description'],  # Informações sobre o usuário
                expansions=['author_id', 'attachments.media_keys']  # Expansões para obter mais detalhes, como autor e mídias
            )

            if not response.data:
                print("Nenhum tweet encontrado com os parâmetros especificados.")
                return pd.DataFrame()  # Retorna um DataFrame vazio se não encontrar tweets
            else:
                attributes_container = []

                for tweet in response.data:
                    tweet_data = {
                        'ID do Usuário': tweet.author_id,
                        'Nome de Usuário': next((user.username for user in response.includes['users'] if user.id == tweet.author_id), None),
                        'Nome Completo': next((user.name for user in response.includes['users'] if user.id == tweet.author_id), None),
                        'Data de Criação': tweet.created_at,
                        'Número de Curtidas': tweet.public_metrics['like_count'],
                        'Número de Retweets': tweet.public_metrics['retweet_count'],
                        'Número de Respostas': tweet.public_metrics['reply_count'],
                        'Texto do Tweet': tweet.text,
                        'Idioma': tweet.lang,
                        'Localização': tweet.geo,
                        'Anotações Contextuais': tweet.context_annotations,
                        'Entidades': tweet.entities,
                        'ID da Conversa': tweet.conversation_id,
                        'Fonte': tweet.source,
                        'Tweets Referenciados': tweet.referenced_tweets if hasattr(tweet, 'referenced_tweets') else None,
                        'Anexos': tweet.attachments
                    }
                    attributes_container.append(tweet_data)

                    output = pd.DataFrame(attributes_container)
                    output['singer'] = search_query

                return pd.DataFrame(attributes_container)

        except tweepy.TweepyException as e:
            if e.response.status_code == 429:
                print("Limite de requisições atingido. Esperando 15 minutos para tentar novamente...")
            else:
                print(f"Erro ao buscar tweets: {e}")
                return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro inesperado
