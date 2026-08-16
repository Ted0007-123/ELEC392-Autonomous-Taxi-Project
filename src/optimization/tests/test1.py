from optimization.graph import MapGraph, Point
from optimization.route_calculator import RouteCalculator


def print_separator(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_case_1(graph, calculator):
    print_separator("TEST 1: Graph Information")

    print("Number of nodes:", len(graph.get_nodes()))
    print("Number of edges:", len(graph.get_edges()))
    print("Number of spawn points:", len(graph.get_spawn_points()))

    print("\nSample node:")
    print(graph.get_node("AQUATIC_FEATHER"))

    print("\nSample spawn point:")
    print(graph.get_spawn_point("P13"))

    print("\nNeighbors of MIGRATION_FEATHER:")
    print(graph.get_neighbors("MIGRATION_FEATHER"))


def test_case_2(graph, calculator):
    print_separator("TEST 2: Projection Test")

    point = Point(2.40, 1.35)
    result = graph.project_point_to_nearest_edge(point)

    print("Input point:", point)
    print("Nearest edge:", result.edge)
    print("Projected point:", result.projected_point)
    print("Distance to edge:", result.distance_to_edge)


def test_case_3(graph, calculator):
    print_separator("TEST 3: Shortest Distance")

    start = Point(2.40, 1.35)
    end = Point(4.35, 2.23)

    distance = calculator.shortest_distance(start, end)

    print("Start:", start)
    print("End:", end)
    print("Shortest distance:", distance)


def test_case_4(graph, calculator):
    print_separator("TEST 4: Shortest Path")

    start = Point(2.40, 1.35)
    end = Point(4.35, 2.23)

    distance, path = calculator.shortest_path(start, end)

    print("Distance:", distance)
    print("Path:")
    for node in path:
        print(" ", node)


def test_case_5(graph, calculator):
    print_separator("TEST 5: Fare Example (current → src → dest)")

    current = Point(2.40, 1.35)
    src = graph.get_spawn_point("P13").point
    dest = graph.get_spawn_point("P18").point

    cost1 = calculator.shortest_distance(current, src)
    cost2 = calculator.shortest_distance(src, dest)

    total_cost = cost1 + cost2

    print("Current position:", current)
    print("Source:", src)
    print("Destination:", dest)

    print("Cost current → src:", cost1)
    print("Cost src → dest:", cost2)
    print("Total cost:", total_cost)


def main():
    graph = MapGraph()
    calculator = RouteCalculator(graph)

    test_case_1(graph, calculator)
    test_case_2(graph, calculator)
    test_case_3(graph, calculator)
    test_case_4(graph, calculator)
    test_case_5(graph, calculator)


if __name__ == "__main__":
    main()