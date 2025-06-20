import streamlit as st
import requests
import os
import openai

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="BetInsight", layout="centered")
st.title("BetInsight 🎯")
st.markdown("**Insights de apostas esportivas gerados por IA**")

competitions = {
    "Brasileirão Série A": "2021",
    "Premier League": "PL",
    "Champions League": "CL"
}

competition = st.selectbox("Selecione o Campeonato", list(competitions.keys()))

@st.cache_data(ttl=300)
def fetch_matches(comp_id):
    url = f"https://api.football-data.org/v2/competitions/{comp_id}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    resp = requests.get(url, headers=headers)
    return resp.json().get("matches", []) if resp.status_code == 200 else []

matches = fetch_matches(competitions[competition])
options = [f"{m['homeTeam']['name']} x {m['awayTeam']['name']} - {m['utcDate'][:10]}" for m in matches]
selected = st.selectbox("Selecione a Partida", options)

if st.button("Gerar Insight de Aposta"):
    idx = options.index(selected)
    match = matches[idx]
    prompt = (
        f"Você é um analista esportivo. Dados da partida:\n"
        f"Casa: {match['homeTeam']['name']}\n"
        f"Visitante: {match['awayTeam']['name']}\n"
        f"Data: {match['utcDate']}\n"
        f"Gere um insight de aposta com probabilidade, sugestão de stake e principais estatísticas."
    )
    with st.spinner("Consultando IA..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é especialista em apostas esportivas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
        )
    st.subheader("🎲 Insight de Aposta")
    st.write(response.choices[0].message.content)
