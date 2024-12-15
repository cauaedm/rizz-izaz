import tweepy
import pandas as pd
import json

def scrap(search_query, no_of_tweets):
    # Carregando a API key do arquivo config.json
    with open('config.json', 'r') as file:
        config = json.load(file)

    bearer_token = config['api_key']

    # Criando o cliente para a API v2
    client = tweepy.Client(bearer_token=bearer_token)

    try:
        # Buscando tweets com os parâmetros definidos
        response = client.search_recent_tweets(
            query=search_query,
            max_results=no_of_tweets,
            tweet_fields=['created_at', 'public_metrics', 'author_id']
        )

        # Verificando se houve resultados
        if not response.data:
            print("Nenhum tweet encontrado com os parâmetros especificados.")
            return None

        # Extraindo alguns atributos do tweet
        attributes_container = [
            [tweet.author_id, tweet.created_at, tweet.public_metrics['like_count'], tweet.text] for tweet in response.data
        ]

        # Definindo os nomes das colunas para o dataframe
        columns = ["User ID", "Date Created", "Number of Likes", "Tweet"]

        # Criando o dataframe
        tweets_df = pd.DataFrame(attributes_container, columns=columns)

        tweets_df.to_csv("tweets_db.csv", index=False)

        return tweets_df

    except tweepy.TweepyException as e:
        print(f"Erro ao buscar tweets: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def get_rate_limit():
    with open('config.json', 'r') as file:
        config = json.load(file)

    bearer_token = config['api_key']

    # Criando o cliente para a API v2
    client = tweepy.Client(bearer_token=bearer_token)

    try:
        response = client.get_rate_limit_status()
        search_limits = response['resources']['search']['/search/tweets']
        return search_limits['limit'], search_limits['remaining']
    except Exception as e:
        return 100, 100  # Valores padrão caso ocorra erro
