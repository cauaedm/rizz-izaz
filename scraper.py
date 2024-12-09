import tweepy
import pandas as pd

# Insira suas credenciais da API do Twitter
api_key = "SUA_API_KEY"
api_key_secret = "SUA_API_SECRET"
access_token = "SEU_ACCESS_TOKEN"
access_token_secret = "SEU_ACCESS_SECRET"

# Autenticação na API
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Função para buscar tweets por palavras-chave
def search_tweets(keywords, count=100):
    """
    Busca tweets com base nas palavras-chave fornecidas.
    Args:
        keywords (list): Lista de palavras-chave.
        count (int): Número máximo de tweets a ser retornado.
    
    Returns:
        DataFrame com os tweets encontrados.
    """
    # Realizar a busca de tweets
    query = " OR ".join(keywords)  # Busca por palavras-chave (com "OR" entre elas)
    tweets = tweepy.Cursor(api.search_tweets, q=query, lang="pt", tweet_mode='extended').items(count)
    
    # Criar uma lista para armazenar dados dos tweets
    tweet_data = []
    
    for tweet in tweets:
        tweet_data.append({
            'id': tweet.id,
            'created_at': tweet.created_at,
            'text': tweet.full_text,
            'user': tweet.user.screen_name,
            'location': tweet.user.location
        })
    
    # Criar um DataFrame com os dados
    df_tweets = pd.DataFrame(tweet_data)
    return df_tweets

# Exemplo de como usar a função
keywords = ["python", "inteligência artificial", "tecnologia"]
df = search_tweets(keywords, count=50)
print(df.head())
