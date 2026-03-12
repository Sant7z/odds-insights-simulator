from typing import List, Dict


def extract_lowest_odds(events: List[Dict]) -> List[Dict]:
    flattened = []

    for event in events:
        home = event.get("home_team")
        away = event.get("away_team")
        commence_time = event.get("commence_time")
        bookmakers = event.get("bookmakers", [])

        best_outcome = None

        for bookmaker in bookmakers:
            markets = bookmaker.get("markets", [])
            for market in markets:
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    price = outcome.get("price")
                    name = outcome.get("name")

                    if price is None:
                        continue

                    if best_outcome is None or price < best_outcome["odd"]:
                        best_outcome = {
                            "match": f"{home} vs {away}",
                            "market_pick": name,
                            "odd": float(price),
                            "bookmaker": bookmaker.get("title", "Unknown"),
                            "commence_time": commence_time,
                        }

        if best_outcome:
            flattened.append(best_outcome)

    return sorted(flattened, key=lambda x: x["odd"])


def build_theoretical_combination(events: List[Dict], quantity: int) -> List[Dict]:
    return events[:quantity]


def calculate_combined_odds(selected_events: List[Dict]) -> float:
    combined = 1.0
    for event in selected_events:
        combined *= float(event["odd"])
    return round(combined, 2)


def calculate_hypothetical_return(stake: float, combined_odds: float) -> float:
    return round(stake * combined_odds, 2)