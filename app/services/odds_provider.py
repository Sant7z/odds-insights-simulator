import requests
from app.config import ODDS_API_BASE_URL, ODDS_API_KEY, DEFAULT_MARKETS, DEFAULT_REGIONS


def fetch_odds(sport: str = "soccer_epl") -> list:
    url = f"{ODDS_API_BASE_URL}/sports/{sport}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": DEFAULT_REGIONS,
        "markets": DEFAULT_MARKETS,
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()