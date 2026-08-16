from optimization import MapGraph, RouteCalculator
from optimization.fare_selector import FareSelector
from optimization.graph import Point


def print_separator(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def get_example_fares():
    return [
        {
            "id": 101,
            "modifiers": 0,
            "src": {"x": 1.70, "y": 0.19},   # P1
            "dest": {"x": 3.03, "y": 1.75},  # P13
            "claimed": False,
            "expiry": 9999999999,
            "pay": 12.0,
            "reputation": 5,
        },
        {
            "id": 102,
            "modifiers": 1,
            "src": {"x": 2.60, "y": 0.19},   # P2
            "dest": {"x": 5.10, "y": 2.83},  # P18
            "claimed": False,
            "expiry": 9999999999,
            "pay": 20.0,
            "reputation": 8,
        },
        {
            "id": 103,
            "modifiers": 2,
            "src": {"x": 3.80, "y": 1.22},   # P6
            "dest": {"x": 4.52, "y": 3.60},  # P21
            "claimed": False,
            "expiry": 9999999999,
            "pay": 9.0,
            "reputation": 9,
        },
        {
            "id": 104,
            "modifiers": 0,
            "src": {"x": 0.28, "y": 2.18},   # P10
            "dest": {"x": 5.85, "y": 3.25},  # P17
            "claimed": False,
            "expiry": 9999999999,
            "pay": 30.0,
            "reputation": 10,
        },
        {
            "id": 105,
            "modifiers": 0,
            "src": {"x": 5.10, "y": 2.23},   # P12
            "dest": {"x": 0.28, "y": 4.00},  # P23
            "claimed": False,
            "expiry": 9999999999,
            "pay": 15.0,
            "reputation": 4,
        },
    ]


def test_case_1_basic_selection(selector):
    print_separator("TEST 1: Basic Fare Selection")

    fares = get_example_fares()
    current_position = Point(2.40, 1.35)

    best_fare_id, best_efficiency = selector.select_best_fare(current_position, fares)

    print("Current position:", current_position)
    print("Best fare id:", best_fare_id)
    print("Best efficiency:", best_efficiency)


def test_case_2_score_all_fares(selector):
    print_separator("TEST 2: Score All Fares")

    fares = get_example_fares()
    current_position = Point(2.40, 1.35)

    scored_fares = selector.score_all_fares(current_position, fares)

    print("Current position:", current_position)
    print("\nRanked fares:")
    for item in scored_fares:
        print(
            "Fare ID:",
            item["id"],
            "| Efficiency:", item["efficiency"],
            "| Pay:", item["pay"],
            "| Reputation:", item["reputation"],
            "| Total Distance:", item["total_distance"],
            "| Total Time:", item["total_time"],
        )


def test_case_3_claimed_and_expired_filtered(selector):
    print_separator("TEST 3: Claimed and Expired Fares Are Ignored")

    fares = get_example_fares()

    fares[0]["claimed"] = True
    fares[1]["expiry"] = 0

    current_position = Point(2.40, 1.35)

    best_fare_id, best_efficiency = selector.select_best_fare(current_position, fares)

    print("Current position:", current_position)
    print("Best fare id after filtering:", best_fare_id)
    print("Best efficiency after filtering:", best_efficiency)

    print("\nRemaining scored fares:")
    scored_fares = selector.score_all_fares(current_position, fares)
    for item in scored_fares:
        print("Fare ID:", item["id"], "| Efficiency:", item["efficiency"])


def test_case_4_nearby_vs_high_reward(selector):
    print_separator("TEST 4: Nearby Fare vs High Reward Fare")

    fares = [
        {
            "id": 201,
            "modifiers": 0,
            "src": {"x": 3.03, "y": 1.75},   # P13
            "dest": {"x": 4.35, "y": 2.23},  # P22
            "claimed": False,
            "expiry": 9999999999,
            "pay": 8.0,
            "reputation": 3,
        },
        {
            "id": 202,
            "modifiers": 0,
            "src": {"x": 0.28, "y": 2.18},   # P10
            "dest": {"x": 5.85, "y": 3.25},  # P17
            "claimed": False,
            "expiry": 9999999999,
            "pay": 30.0,
            "reputation": 10,
        },
    ]

    current_position = Point(3.00, 1.60)

    scored_fares = selector.score_all_fares(current_position, fares)
    best_fare_id, best_efficiency = selector.select_best_fare(current_position, fares)

    print("Current position:", current_position)
    print("Best fare id:", best_fare_id)
    print("Best efficiency:", best_efficiency)

    print("\nDetailed scores:")
    for item in scored_fares:
        print(
            "Fare ID:",
            item["id"],
            "| Efficiency:", item["efficiency"],
            "| Total Distance:", item["total_distance"],
            "| Pay:", item["pay"],
            "| Reputation:", item["reputation"],
        )


def test_case_5_different_current_positions(selector):
    print_separator("TEST 5: Same Fares, Different Current Positions")

    fares = get_example_fares()

    test_positions = [
        Point(2.40, 1.35),
        Point(5.40, 2.30),
        Point(0.40, 3.50),
    ]

    for index, current_position in enumerate(test_positions, start=1):
        best_fare_id, best_efficiency = selector.select_best_fare(current_position, fares)
        print(
            f"Case {index}:",
            "Current position =", current_position,
            "| Best fare id =", best_fare_id,
            "| Best efficiency =", best_efficiency,
        )


def main():
    graph = MapGraph()
    calculator = RouteCalculator(graph)
    selector = FareSelector(calculator)

    test_case_1_basic_selection(selector)
    test_case_2_score_all_fares(selector)
    test_case_3_claimed_and_expired_filtered(selector)
    test_case_4_nearby_vs_high_reward(selector)
    test_case_5_different_current_positions(selector)


if __name__ == "__main__":
    main()