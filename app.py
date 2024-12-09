import streamlit as st
import pandas as pd

from firebase import fetch_data_from_firestore

st.title("Dashboard Twitter Scraper and Analysis - UFRJ Consulting Club")

df = fetch_data_from_firestore('tweets')
st.dataframe(df)