import streamlit as st
import pandas as pd

st.title("Dashboard Twitter Scraper and Analysis - UFRJ Consulting Club")

df = pd.read_csv('tweets.csv')
st.dataframe(df)