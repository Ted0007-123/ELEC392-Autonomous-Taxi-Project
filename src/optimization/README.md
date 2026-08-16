# Optimization Module

This folder handles taxi decision making.

It chooses the best fare and computes the route needed to serve that fare.

---

# File Structure

optimization/
│
├── graph.py
├── route_calculator.py
├── fare_selector.py
├── optimization_interface.py
└── README.md

---

# Purpose of Each File

## graph.py
Map definition.

Contains:
- Nodes
- Directed edges
- Spawn points
- Nearest-road projection logic

Must provide:
- `get_node(name)`
- `get_nodes()`
- `get_neighbors(node_name)`
- `edge_length(edge)`
- `project_point_to_nearest_edge(point)` or `find_closest_edge(point)`

## route_calculator.py
Routing engine.

Main functions:
- `shortest_distance(start_point, end_point)`
- `shortest_path(start_point, end_point)`

Responsibilities:
- Project arbitrary points onto the road network
- Run shortest path search on the directed graph
- Return path cost and node path

## fare_selector.py
Fare scoring engine.

Main functions:
- `prepare_fare_metrics(current_position, fares)`
- `score_prepared_fares(prepared_fares)`
- `select_best_prepared_fare(prepared_fares)`
- `select_best_fare(current_position, fares)`

Responsibilities:
- Filter unavailable fares
- Compute efficiency score
- Rank fares

Does NOT:
- Call VPFS
- Claim fares

## optimization_interface.py
Main external entry point.

This is the file other modules should use.

Responsibilities:
- Read current position from VPFS
- Read fares from VPFS
- Compute fare metrics
- Select best fare
- Claim best fare
- Return route information

---

# External Usage

```python
from optimization.optimization_interface import OptimizationInterface

interface = OptimizationInterface()
result = interface.request_fare()

if result is not None:
    print(result["fare_id"])
    print(result["path_to_pickup"])
    print(result["path_to_destination"])