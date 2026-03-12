# Odds Insights Simulator

Projeto em Python para análise de odds esportivas com dashboard interativo.

## Funcionalidades

- Consumo de API externa de odds
- Seleção automática das menores odds
- Geração de combinação teórica simulada
- Cálculo de odd combinada
- Cálculo de retorno hipotético
- Histórico salvo em SQLite
- Dashboard interativo com Streamlit

## Stack

- Python
- Requests
- Pandas
- Plotly
- Streamlit
- SQLite

## Como rodar

```bash
git clone <url-do-repo>
cd odds-insights-simulator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env