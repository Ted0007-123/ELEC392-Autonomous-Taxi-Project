from optimization.graph import MapGraph, Point
from optimization.route_calculator import RouteCalculator
from optimization.fare_selector import FareSelector


def main():
    print("=" * 60)
    print("TEST 3: Prepared Fare Scoring")
    print("=" * 60)

    graph = MapGraph()
    calculator = RouteCalculator(graph)
    selector = FareSelector(calculator)

    current_position = Point(2.4, 1.35)

    # example fares (VPFS format)
    fares = [
        {
            "id": 1,
            "src": {"x": 3.03, "y": 1.75},
            "dest": {"x": 5.10, "y": 2.83},
            "pay": 20,
            "reputation": 5,
            "claimed": False,
        },
        {
            "id": 2,
            "src": {"x": 1.70, "y": 0.19},
            "dest": {"x": 5.85, "y": 3.25},
            "pay": 35,
            "reputation": 2,
            "claimed": False,
        },
        {
            "id": 3,
            "src": {"x": 0.80, "y": 1.22},
            "dest": {"x": 5.25, "y": 3.92},
            "pay": 15,
            "reputation": 10,
            "claimed": False,
        },
    ]

    # STEP 1: prepare raw metrics (normally done in optimization_interface)
    prepared = selector._prepare_fare_metrics(current_position, fares)

    print("\nPrepared fares:")
    for f in prepared:
        print(
            f"id={f['id']}, "
            f"dist={f['total_distance']:.3f}, "
            f"time={f['total_time']:.3f}"
        )

    # STEP 2: scoring (NEW FUNCTION)
    scored = selector.score_prepared_fares(prepared)

    print("\nRanked fares:")
    for f in scored:
        print(
            f"id={f['id']}, "
            f"eff={f['efficiency']:.4f}, "
            f"pay_norm={f['pay_norm']:.3f}, "
            f"dist_norm={f['distance_norm']:.3f}"
        )

    # STEP 3: best fare
    best_id, best_eff = selector.select_best_prepared_fare(prepared)

    print("\nBest fare:")
    print(f"id={best_id}, efficiency={best_eff:.4f}")


if __name__ == "__main__":
    main()