import streamlit as st
import pandas as pd

st.set_page_config(page_title="Capnalyx", layout="wide")

st.title("🚀 Capnalyx - AI Investment Platform")

st.write("Upload your startup CSV file")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("File Uploaded Successfully ✅")
    st.dataframe(df)

    st.subheader("Basic Analysis")
    st.write(df.describe())
