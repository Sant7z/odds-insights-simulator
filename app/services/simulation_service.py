from app.services.analytics import (
    build_theoretical_combination,
    calculate_combined_odds,
    calculate_hypothetical_return,
)


def generate_simulation(events: list, quantity: int, stake: float) -> dict:
    selected = build_theoretical_combination(events, quantity)
    combined_odds = calculate_combined_odds(selected)
    hypothetical_return = calculate_hypothetical_return(stake, combined_odds)

    return {
        "selected_events": selected,
        "combined_odds": combined_odds,
        "stake": stake,
        "hypothetical_return": hypothetical_return,
    }