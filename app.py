import streamlit as st
import requests
import openai

# Carregar chaves de ambiente via st.secrets
FOOTBALL_DATA_API_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
OPENAI_API_KEY        = st.secrets["OPENAI_API_KEY"]
openai.api_key        = OPENAI_API_KEY

# Configuração da página
st.set_page_config(page_title="BetInsight", layout="centered")
st.title("BetInsight 🎯")
st.markdown("**Insights de apostas esportivas gerados por IA**")

# Mapeamento de campeonatos para a API
competitions = {
    "Brasileirão Série A": "2021",
    "Premier League":      "PL",
    "Champions League":    "CL",
}

# Seleção do campeonato
competition = st.selectbox("Selecione o Campeonato", list(competitions.keys()))

@st.cache_data(ttl=300)
def fetch_matches(comp_id):
    """Retorna lista de partidas agendadas para o campeonato dado."""
    url = f"https://api.football-data.org/v2/competitions/{comp_id}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        st.error(f"Erro ao buscar partidas: status {resp.status_code}")
        return []
    data = resp.json().get("matches", [])
    return data

# Busca as partidas
matches = fetch_matches(competitions[competition])

# Se não houver partidas, informe o usuário
if not matches:
    st.warning("No momento não há partidas agendadas para este campeonato.")
else:
    # Monta as opções de dropdown
    options = [
        f"{m['homeTeam']['name']} x {m['awayTeam']['name']} — {m['utcDate'][:10]}"
        for m in matches
    ]
    selected = st.selectbox("Selecione a Partida", options)

    # Só exibe o botão se algo estiver selecionado
    if selected and st.button("Gerar Insight de Aposta"):
        try:
            idx   = options.index(selected)
            match = matches[idx]

            # Prepara o prompt para a OpenAI
            prompt = (
                f"Você é um analista esportivo. Dados da partida:\n"
                f"Casa: {match['homeTeam']['name']}\n"
                f"Visitante: {match['awayTeam']['name']}\n"
                f"Data: {match['utcDate']}\n"
                "Gere um insight de aposta com probabilidade, sugestão de stake e principais estatísticas."
            )

            # Chama a OpenAI
            with st.spinner("Consultando IA..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é especialista em apostas esportivas."},
                        {"role": "user",   "content": prompt}
                    ],
                    max_tokens=250,
                )

            # Exibe o resultado
            st.subheader("🎲 Insight de Aposta")
            st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Erro ao gerar insight: {e}")
