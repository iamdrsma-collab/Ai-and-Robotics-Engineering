"""
AI.101 — Introduction to Artificial Intelligence
Module 01 Practical Demonstration: Utility-Based Warehouse Robot Agent
"""


def sense_environment(distance_m: float, battery_pct: int, path_clear: bool) -> dict:
    """Read sensor values into a clean dictionary."""
    return {
        "distance_m": distance_m,
        "battery_pct": battery_pct,
        "path_clear": path_clear,
    }


def score_action(action: str, percept: dict) -> float:
    """Calculate utility score: U = (w_s * Safety) + (w_p * Speed) - (w_e * Energy)."""
    w_s, w_p, w_e = 5.0, 3.0, 1.0

    if action == "STOP_AND_WAIT":
        safety = 10.0 if percept["distance_m"] < 1.5 else 6.0
        speed, energy = 0.0, 0.5
    elif action == "SLOW_AROUND":
        safety = 8.5 if percept["distance_m"] >= 1.5 else 2.0
        speed, energy = 5.0, 2.0
    elif action == "FAST_FORWARD":
        is_safe = percept["path_clear"] and percept["distance_m"] > 3.0 and percept["battery_pct"] >= 20
        safety = 9.0 if is_safe else 1.0
        speed, energy = 9.5, 4.0
    elif action == "GO_CHARGE":
        safety = 9.0
        speed = 8.0 if percept["battery_pct"] < 20 else 1.0
        energy = 1.0
    else:
        return -999.0

    return round((w_s * safety) + (w_p * speed) - (w_e * energy), 2)


def choose_best_action(percept: dict) -> tuple[str, dict]:
    """Evaluate every possible action and pick the highest utility score."""
    actions = ["STOP_AND_WAIT", "SLOW_AROUND", "FAST_FORWARD", "GO_CHARGE"]
    scores = {act: score_action(act, percept) for act in actions}
    best = max(scores, key=scores.get)
    return best, scores


if __name__ == "__main__":
    scenarios = [
        ("Open Corridor", sense_environment(distance_m=5.0, battery_pct=85, path_clear=True)),
        ("Worker Nearby", sense_environment(distance_m=1.1, battery_pct=70, path_clear=False)),
        ("Low Battery", sense_environment(distance_m=4.0, battery_pct=14, path_clear=True)),
    ]

    for name, data in scenarios:
        chosen, all_scores = choose_best_action(data)
        print(f"Scenario: {name}")
        print(f"  Sensors : {data}")
        print(f"  Scores  : {all_scores}")
        print(f"  Decision: -> {chosen}\n")
