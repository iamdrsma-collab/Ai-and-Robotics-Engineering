"""
AI.101 — Introduction to Artificial Intelligence
Module 01 Guided Laboratory Exercise: Smart Room Cooling & Cleaning Agent

STUDENT TASKS:
1. Run this script and inspect how the agent chooses actions across four room states.
2. Adjust the weights (w_comfort, w_clean, w_energy) inside score_room_action()
   so the robot prioritizes energy saving when battery is below 25 percent.
3. Add a fifth test scenario where temperature is 31.0 C AND a person is sleeping
   (quiet_mode = True), and verify the agent chooses ECO_FAN instead of noisy VACUUM.
"""


def read_room_sensors(temp_c: float, dust_level: int, battery_pct: int, quiet_mode: bool) -> dict:
    return {
        "temp_c": temp_c,
        "dust_level": dust_level,       # 0 (clean) to 10 (very dusty)
        "battery_pct": battery_pct,     # 0 to 100
        "quiet_mode": quiet_mode,
    }


def score_room_action(action: str, s: dict) -> float:
    w_comfort, w_clean, w_energy = 4.0, 3.0, 1.5

    if action == "COOL_HIGH":
        comfort = 9.5 if (s["temp_c"] > 28.0 and not s["quiet_mode"]) else 3.0
        clean, energy = 0.0, 5.0
    elif action == "ECO_FAN":
        comfort = 8.0 if s["temp_c"] > 25.0 else 4.0
        clean, energy = 0.0, 1.5
    elif action == "VACUUM_FLOOR":
        if s["quiet_mode"] or s["battery_pct"] < 25:
            comfort, clean, energy = 0.0, 2.0, 6.0
        else:
            comfort = 5.0
            clean = float(s["dust_level"])
            energy = 4.5
    elif action == "DOCK_AND_CHARGE":
        comfort = 5.0
        clean = 8.0 if s["battery_pct"] < 25 else 1.0
        energy = 0.2
    else:
        return -999.0

    return round((w_comfort * comfort) + (w_clean * clean) - (w_energy * energy), 2)


def run_lab_simulation() -> None:
    room_tests = [
        ("Hot Afternoon", read_room_sensors(30.5, dust_level=2, battery_pct=90, quiet_mode=False)),
        ("Dusty Morning", read_room_sensors(23.0, dust_level=9, battery_pct=80, quiet_mode=False)),
        ("Quiet Study Hour", read_room_sensors(27.5, dust_level=8, battery_pct=75, quiet_mode=True)),
        ("Low Battery Alert", read_room_sensors(24.0, dust_level=6, battery_pct=18, quiet_mode=False)),
    ]

    actions = ["COOL_HIGH", "ECO_FAN", "VACUUM_FLOOR", "DOCK_AND_CHARGE"]
    for label, sensors in room_tests:
        scores = {a: score_room_action(a, sensors) for a in actions}
        winner = max(scores, key=scores.get)
        print(f"[{label}] -> Chosen Action: {winner} | Scores: {scores}")


if __name__ == "__main__":
    run_lab_simulation()
