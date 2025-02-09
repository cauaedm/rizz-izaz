import pandas as pd
import google.generativeai as genai
import time
import configparser
import streamlit as st

class Sentiment:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        api_key = config["GeminiAPI"]["bearer_token"]
        genai.configure(api_key=api_key)  # Substitua com sua chave real
        self.progress_bar = st.progress(0)
        pass

    def analyse(self, df):
        def create_group_sentiment_prompt(tweets):
            prompt = "Analise os seguintes tweets e diga se o sentimento de cada um é 'positivo' ou 'negativo'. Responda em uma lista, mantendo a ordem:\n\n"
            for i, tweet in enumerate(tweets):
                prompt += f"{i+1}. '{tweet}'\n"
            prompt += "\nResponda apenas com 'positivo' ou 'negativo' para cada tweet, um por linha."
            return prompt

        # Função para enviar o prompt ao Gemini e obter as respostas para o grupo de tweets
        def get_group_sentiment_from_gemini(tweets):
            try:
                model = genai.GenerativeModel("gemini-pro")
                prompt = create_group_sentiment_prompt(tweets)
                response = model.generate_content(prompt)
                sentiments = response.text.strip().lower().split("\n")
                # Converte respostas em 1 (positivo) e -1 (negativo)
                results = [1 if "positivo" in sentiment else -1 for sentiment in sentiments]
                return results
            except Exception as e:
                print(f"Erro ao processar os tweets: {tweets}. Erro: {e}")
                return [None] * len(tweets)

        # Função principal para adicionar a análise de sentimento ao DataFrame
        def add_sentiment_analysis_to_df(df, text_column, batch_size=5):
            sentiment_results = []
            sleep_time = 0.5  # Tempo inicial de espera

            for start in range(0, len(df), batch_size):
                batch = df[text_column][start:start + batch_size].tolist()
                self.progress_bar.progress((start+1) / len(df))
                print(f"Analisando tweets {start + 1} a {min(start + batch_size, len(df))}...")

                while True:  # Loop para re-tentar após erro 429
                    try:
                        batch_sentiments = get_group_sentiment_from_gemini(batch)
                        sentiment_results.extend(batch_sentiments)
                        time.sleep(sleep_time)
                        break  # Sai do loop se o processamento for bem-sucedido
                    except Exception as e:
                        if "429" in str(e):  # Detecta o erro de quota esgotada
                            print(f"Erro 429 detectado. Aumentando o tempo de espera para {sleep_time} segundos...")
                            sleep_time *= 2  # Aumenta o tempo de espera exponencialmente
                            time.sleep(sleep_time)
                        else:
                            print(f"Erro inesperado: {e}. Adicionando valores nulos ao batch.")
                            sentiment_results.extend([None] * len(batch))  # Adiciona Nones em caso de erro
                            break

            df["sentimento"] = sentiment_results
            return df
        
        return add_sentiment_analysis_to_df(df, text_column="text", batch_size=5)