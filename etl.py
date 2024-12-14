import pandas as pd

def read_data(path):
    return pd.read_csv(f"{path}")

def preprocess(path): 

    df = read_data(path)

    df['singer'] = "Duda Beat"

    df['date'] = pd.to_datetime(df['date'])

    return df

def write_data(df, path):
    df.to_csv(f"{path}", index=False)