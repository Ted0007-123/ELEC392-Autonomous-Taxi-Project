from __future__ import annotations

import heapq
from math import hypot
from typing import Dict, List, Optional, Tuple

from .graph import Edge, MapGraph, Point


class RouteCalculator:
    def __init__(self, graph: MapGraph) -> None:
        self.graph = graph

    def _distance(self, a: Point, b: Point) -> float:
        return hypot(b.x - a.x, b.y - a.y)

    def _project_point_to_nearest_edge(self, point: Point):
        if hasattr(self.graph, "project_point_to_nearest_edge"):
            return self.graph.project_point_to_nearest_edge(point)
        if hasattr(self.graph, "find_closest_edge"):
            return self.graph.find_closest_edge(point)
        raise AttributeError(
            "MapGraph must provide project_point_to_nearest_edge(point) or find_closest_edge(point)"
        )

    def _edge_length(self, edge: Edge) -> float:
        if hasattr(self.graph, "edge_length"):
            return self.graph.edge_length(edge)
        start = self.graph.get_node(edge.start)
        end = self.graph.get_node(edge.end)
        return self._distance(start, end)

    def _dijkstra(
        self,
        start_node: str,
        end_node: str,
    ) -> Tuple[float, List[str]]:
        if start_node == end_node:
            return 0.0, [start_node]

        distances: Dict[str, float] = {
            node_name: float("inf") for node_name in self.graph.get_nodes()
        }
        previous: Dict[str, Optional[str]] = {
            node_name: None for node_name in self.graph.get_nodes()
        }

        distances[start_node] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, start_node)]

        while heap:
            current_distance, current_node = heapq.heappop(heap)

            if current_distance > distances[current_node]:
                continue

            if current_node == end_node:
                break

            neighbors = self.graph.get_neighbors(current_node)
            for neighbor, weight in neighbors.items():
                candidate = current_distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = current_node
                    heapq.heappush(heap, (candidate, neighbor))

        if distances[end_node] == float("inf"):
            return float("inf"), []

        path: List[str] = []
        cursor: Optional[str] = end_node
        while cursor is not None:
            path.append(cursor)
            cursor = previous[cursor]
        path.reverse()

        return distances[end_node], path

    def shortest_path(
        self,
        start_point: Point,
        end_point: Point,
    ) -> Tuple[float, List[str]]:
        start_projection = self._project_point_to_nearest_edge(start_point)
        end_projection = self._project_point_to_nearest_edge(end_point)

        start_edge = start_projection.edge
        end_edge = end_projection.edge

        start_projected_point = start_projection.projected_point
        end_projected_point = end_projection.projected_point

        candidates: List[Tuple[float, List[str]]] = []

        start_edge_total = self._edge_length(start_edge)
        end_edge_total = self._edge_length(end_edge)

        start_to_start_node = self._distance(start_point, start_projected_point) + self._distance(
            start_projected_point, self.graph.get_node(start_edge.start)
        )
        start_to_end_node = self._distance(start_point, start_projected_point) + self._distance(
            start_projected_point, self.graph.get_node(start_edge.end)
        )

        end_from_start_node = self._distance(
            end_projected_point, self.graph.get_node(end_edge.start)
        ) + self._distance(end_projected_point, end_point)
        end_from_end_node = self._distance(
            end_projected_point, self.graph.get_node(end_edge.end)
        ) + self._distance(end_projected_point, end_point)

        start_options = [
            (start_edge.start, start_to_start_node),
            (start_edge.end, start_to_end_node),
        ]
        end_options = [
            (end_edge.start, end_from_start_node),
            (end_edge.end, end_from_end_node),
        ]

        for start_node, start_cost in start_options:
            for end_node, end_cost in end_options:
                graph_distance, node_path = self._dijkstra(start_node, end_node)
                if graph_distance == float("inf"):
                    continue

                total_distance = start_cost + graph_distance + end_cost

                if not node_path:
                    continue

                candidates.append((total_distance, node_path))

        if start_edge.start == end_edge.start and start_edge.end == end_edge.end:
            direct_distance = self._distance(start_point, start_projected_point)
            direct_distance += self._distance(start_projected_point, end_projected_point)
            direct_distance += self._distance(end_projected_point, end_point)
            candidates.append((direct_distance, [start_edge.start, start_edge.end]))

        if not candidates:
            return float("inf"), []

        best_distance, best_path = min(candidates, key=lambda item: item[0])
        return best_distance, best_path

    def shortest_distance(
        self,
        start_point: Point,
        end_point: Point,
    ) -> float:
        distance, _ = self.shortest_path(start_point, end_point)
        return distance