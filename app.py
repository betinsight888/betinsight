import streamlit as st
import requests
import openai

# ─── Carregar chaves de ambiente via st.secrets ────────────────────────────────
FOOTBALL_DATA_API_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
OPENAI_API_KEY        = st.secrets["OPENAI_API_KEY"]
openai.api_key        = OPENAI_API_KEY

# ─── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="BetInsight", layout="centered")
st.title("BetInsight 🎯")
st.markdown("**Insights de apostas esportivas gerados por IA**")

# ─── Mapeamento de campeonatos para seus IDs oficiais na API ────────────────
competitions = {
    "Brasileirão Série A": "2013",   # ID correto
    "Premier League":      "2021",   # ID correto
    "Champions League":    "2001",   # ID correto
}

# ─── Seleção do campeonato ──────────────────────────────────────────────────
competition = st.selectbox("Selecione o Campeonato", list(competitions.keys()))

@st.cache_data(ttl=300)
def fetch_matches(comp_id: str):
    """Retorna lista de partidas agendadas para o ID de campeonato fornecido."""
    url = f"https://api.football-data.org/v2/competitions/{comp_id}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        st.error(f"Erro ao buscar partidas: status {resp.status_code}")
        return []
    return resp.json().get("matches", [])

# ─── Busca as partidas ──────────────────────────────────────────────────────
matches = fetch_matches(competitions[competition])

# ─── Lógica de exibição e geração de insight ────────────────────────────────
if not matches:
    st.warning("No momento não há partidas agendadas para este campeonato.")
else:
    options = [
        f"{m['homeTeam']['name']} x {m['awayTeam']['name']} — {m['utcDate'][:10]}"
        for m in matches
    ]
    selected = st.selectbox("Selecione a Partida", options)

    if selected and st.button("Gerar Insight de Aposta"):
        idx = options.index(selected)
        match = matches[idx]

        # Monta o prompt para a IA
        prompt = (
            f"Você é um analista esportivo. Dados da partida:\n"
            f"Casa: {match['homeTeam']['name']}\n"
            f"Visitante: {match['awayTeam']['name']}\n"
            f"Data: {match['utcDate']}\n"
            "Gere um insight de aposta com probabilidade, sugestão de stake e principais estatísticas."
        )

        with st.spinner("Consultando IA..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",  "content": "Você é especialista em apostas esportivas."},
                    {"role": "user",    "content": prompt}
                ],
                max_tokens=250,
            )
        st.subheader("🎲 Insight de Aposta")
        st.write(response.choices[0].message.content)
