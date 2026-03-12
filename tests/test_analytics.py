from app.services.analytics import calculate_combined_odds


def test_calculate_combined_odds():
    events = [
        {"odd": 1.20},
        {"odd": 1.50},
        {"odd": 1.30},
    ]
    assert calculate_combined_odds(events) == 2.34