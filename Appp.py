import streamlit as st

st.title("My First Website 🎉")
st.write("Welcome! This is my web page.")

name = st.text_input("Enter your name")

if name:
    st.write(f"Hello {name} 😊")
