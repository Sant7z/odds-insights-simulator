import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
import plotly.express as px
import requests

from app.db.connection import init_db
from app.db.repository import save_simulation, list_simulations
from app.services.odds_provider import fetch_odds
from app.services.analytics import extract_lowest_odds
from app.services.simulation_service import generate_simulation


def format_datetime(value: str) -> str:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return value


def add_probability_columns(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty and "odd" in df.columns:
        df["odd"] = df["odd"].astype(float).round(2)
        df["probabilidade_implícita (%)"] = (1 / df["odd"] * 100).round(2)
    return df


st.set_page_config(
    page_title="Odds Insights Simulator",
    page_icon="📊",
    layout="wide"
)

init_db()

st.title("📊 Odds Insights Simulator")
st.caption(
    "Simulador analítico com consumo de API externa, cálculo de combinação teórica e histórico local em SQLite."
)

with st.sidebar:
    st.header("Configurações")

    sport = st.text_input(
        "Esporte / Liga",
        value="soccer_epl",
        help="Exemplo: soccer_epl, basketball_nba, soccer_brazil_campeonato"
    )

    quantity = st.slider(
        "Quantidade de eventos",
        min_value=2,
        max_value=10,
        value=3
    )

    stake = st.number_input(
        "Valor hipotético",
        min_value=1.0,
        value=10.0,
        step=1.0
    )

    st.markdown("---")
    st.info(
        "A combinação exibida é teórica e baseada nos eventos selecionados automaticamente pelo sistema."
    )

if "last_simulation" not in st.session_state:
    st.session_state["last_simulation"] = None

if st.button("Buscar odds e gerar simulação", use_container_width=True):
    try:
        with st.spinner("Buscando dados da API..."):
            raw_events = fetch_odds(sport)
            ranked_events = extract_lowest_odds(raw_events)
            simulation = generate_simulation(ranked_events, quantity, stake)

        if not ranked_events:
            st.warning("Nenhum evento encontrado para os filtros informados.")
        else:
            st.session_state["last_simulation"] = {
                "sport": sport,
                "ranked_events": ranked_events,
                "simulation": simulation,
            }

            save_simulation(
                sport=sport,
                requested_events=quantity,
                combined_odds=simulation["combined_odds"],
                stake=simulation["stake"],
                hypothetical_return=simulation["hypothetical_return"],
                events=simulation["selected_events"],
            )

            st.success("Simulação gerada e salva no histórico com sucesso.")

    except requests.exceptions.HTTPError as e:
        st.error(f"Erro HTTP ao consultar a API: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com a API: {e}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")

data = st.session_state.get("last_simulation")

if data:
    ranked_events = data["ranked_events"]
    simulation = data["simulation"]

    selected_df = pd.DataFrame(simulation["selected_events"])
    ranked_df = pd.DataFrame(ranked_events)

    selected_df = add_probability_columns(selected_df)
    ranked_df = add_probability_columns(ranked_df)

    if "commence_time" in selected_df.columns:
        selected_df["commence_time"] = selected_df["commence_time"].apply(format_datetime)

    if "commence_time" in ranked_df.columns:
        ranked_df["commence_time"] = ranked_df["commence_time"].apply(format_datetime)

    st.subheader("Resumo da simulação")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Eventos analisados", len(ranked_df))
    col2.metric("Eventos selecionados", len(selected_df))
    col3.metric("Odd combinada teórica", f"{simulation['combined_odds']:.2f}")
    col4.metric("Retorno hipotético", f"R$ {simulation['hypothetical_return']:.2f}")

    st.markdown("---")

    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("Eventos selecionados")

        display_columns = [
            col for col in [
                "match",
                "market_pick",
                "odd",
                "probabilidade_implícita (%)",
                "bookmaker",
                "commence_time",
            ] if col in selected_df.columns
        ]

        st.dataframe(
            selected_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

    with right:
        st.subheader("Melhor resumo rápido")

        min_odd = ranked_df["odd"].min() if not ranked_df.empty else 0
        max_prob = ranked_df["probabilidade_implícita (%)"].max() if not ranked_df.empty else 0

        st.markdown(f"**Menor odd encontrada:** {min_odd:.2f}")
        st.markdown(f"**Maior probabilidade implícita:** {max_prob:.2f}%")
        st.markdown(f"**Valor hipotético usado:** R$ {simulation['stake']:.2f}")

    st.markdown("---")

    if not selected_df.empty:
        st.subheader("Odds dos eventos selecionados")

        fig = px.bar(
            selected_df,
            x="odd",
            y="match",
            orientation="h",
            hover_data=["market_pick", "bookmaker", "probabilidade_implícita (%)"],
            title="Comparativo das odds selecionadas"
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            height=420,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    if not ranked_df.empty:
        st.subheader("Distribuição das odds analisadas")

        dist_fig = px.histogram(
            ranked_df,
            x="odd",
            nbins=20,
            title="Distribuição de odds",
        )

        dist_fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        st.plotly_chart(dist_fig, use_container_width=True)

        st.subheader("Top 5 eventos com maior probabilidade implícita")

        top_safe = ranked_df.sort_values(by="odd", ascending=True).head(5)

        safe_columns = [
            col for col in [
                "match",
                "market_pick",
                "odd",
                "probabilidade_implícita (%)",
                "bookmaker",
                "commence_time",
            ] if col in top_safe.columns
        ]

        st.dataframe(
            top_safe[safe_columns],
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")
st.subheader("Cupom visual da simulação")

if data and st.button("Gerar cupom visual", use_container_width=True):
    selected_events = simulation["selected_events"]

    html = """
<div style="background:#0f172a;border-radius:20px;padding:24px;border:1px solid #1f2937;box-shadow:0 12px 35px rgba(0,0,0,0.35);max-width:420px;margin:auto;font-family:monospace;color:white;">
<div style="text-align:center;font-size:18px;font-weight:700;margin-bottom:14px;">
📊 SIMULAÇÃO ANALÍTICA
</div>

<div style="border-top:1px dashed #475569;border-bottom:1px dashed #475569;padding-top:14px;padding-bottom:14px;">
"""

    for event in selected_events:
        prob = round((1 / float(event["odd"])) * 100, 2)

        html += f"""
<div style="margin-bottom:14px;">
<div style="font-size:15px;font-weight:600;">
⚽ {event["match"]}
</div>
<div style="font-size:13px;color:#cbd5e1;">
Pick: {event["market_pick"]}
</div>
<div style="font-size:13px;color:#cbd5e1;">
Odd: {float(event["odd"]):.2f} | Prob: {prob:.2f}%
</div>
</div>
"""

    html += """
</div>
"""

    html += f"""
<div style="margin-top:16px;font-size:14px;">
<div style="margin-bottom:6px;">
Odd combinada: <b>{simulation['combined_odds']:.2f}</b>
</div>
<div style="margin-bottom:6px;">
Stake: <b>R$ {simulation['stake']:.2f}</b>
</div>
<div style="font-size:16px;font-weight:700;color:#22c55e;">
Retorno hipotético: R$ {simulation['hypothetical_return']:.2f}
</div>
</div>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


st.markdown("---")
st.subheader("Histórico de simulações")

history = list_simulations()

if history:
    history_df = pd.DataFrame(history)

    if "created_at" in history_df.columns:
        history_df["created_at"] = history_df["created_at"].apply(format_datetime)

    history_df = history_df.rename(columns={
        "id": "ID",
        "created_at": "Data",
        "sport": "Esporte",
        "requested_events": "Qtd. eventos",
        "combined_odds": "Odd combinada",
        "stake": "Valor",
        "hypothetical_return": "Retorno hipotético",
    })

    for col in ["Odd combinada", "Valor", "Retorno hipotético"]:
        if col in history_df.columns:
            history_df[col] = history_df[col].astype(float).round(2)

    history_columns = [
        col for col in [
            "ID",
            "Data",
            "Esporte",
            "Qtd. eventos",
            "Odd combinada",
            "Valor",
            "Retorno hipotético",
        ] if col in history_df.columns
    ]

    st.dataframe(
        history_df[history_columns],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhuma simulação salva ainda.")