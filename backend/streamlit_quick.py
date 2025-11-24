import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_URL", "http://localhost:8000")

st.title("Cleo — Quick Prototype (Streamlit)")
learner_id = st.text_input("Learner ID", "demo_learner")
text = st.text_area("Question / message")
if st.button("Envoyer"):
    if not text.strip():
        st.warning("Entrer un texte")
    else:
        resp = requests.post(f"{API}/api/query", json={"learner_id": learner_id, "text": text, "mode": "explain", "top_k": 3})
        st.json(resp.json())