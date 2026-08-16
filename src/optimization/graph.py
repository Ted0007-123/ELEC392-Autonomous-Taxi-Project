from __future__ import annotations

from dataclasses import dataclass
from math import hypot, atan2, degrees
from typing import Dict, List


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Edge:
    start: str
    end: str


@dataclass(frozen=True)
class ProjectionResult:
    edge: Edge
    projected_point: Point
    distance_to_edge: float
    distance_from_start: float
    distance_to_end: float


@dataclass(frozen=True)
class SpawnPoint:
    label: str
    point: Point
    edge: Edge


class MapGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Point] = self._build_nodes()
        self.edges: List[Edge] = self._build_edges()
        self.adjacency: Dict[str, Dict[str, float]] = self._build_adjacency()
        self.spawn_points: Dict[str, SpawnPoint] = self._build_spawn_points()

    def _build_nodes(self) -> Dict[str, Point]:
        return {
            "AQUATIC_BEAK": Point(448, 19),
            "AQUATIC_FEATHER": Point(303, 19),
            "AQUATIC_WADDLE": Point(127, 19),
            "AQUATIC_WATERFOUL": Point(213, 19),
            "BREADCRUMB_CIRCLE": Point(284, 383),
            "BREADCRUMB_WADDLE": Point(181, 449),
            "CIRCLE_FEATHER": Point(305, 286),
            "CIRCLE_WATERFOUL": Point(273, 297),
            "DABBLER_BEAK": Point(452, 283),
            "DABBLER_CIRCLE": Point(350, 314),
            "DABBLER_MALLARD": Point(585, 283),
            "DRAKE_BEAK": Point(452, 392),
            "DRAKE_MALLARD": Point(576, 344),
            "DUCKLING_MALLARD": Point(593, 344),
            "MIGRATION_BEAK": Point(452, 122),
            "MIGRATION_FEATHER": Point(303, 122),
            "MIGRATION_MALLARD": Point(583, 122),
            "MIGRATION_QUACK": Point(31, 122),
            "MIGRATION_WADDLE": Point(126, 122),
            "MIGRATION_WATERFOUL": Point(213, 122),
            "PONDSIDE_BEAK": Point(452, 223),
            "PONDSIDE_FEATHER": Point(305, 223),
            "PONDSIDE_MALLARD": Point(585, 223),
            "PONDSIDE_QUACK": Point(28, 319),
            "PONDSIDE_WADDLE": Point(157, 256),
            "PONDSIDE_WATERFOUL": Point(214, 231),
            "TAIL_BEAK": Point(452, 455),
            "TAIL_CIRCLE": Point(335, 377),
            "TOP_LEFT": Point(39, 435),
            "TOP_RIGHT": Point(576, 435),
            "BOTTOM_LEFT": Point(39, 36),
            "BOTTOM_RIGHT": Point(576, 36),
        }

    def _build_edges(self) -> List[Edge]:
        return [
            Edge("AQUATIC_WADDLE", "AQUATIC_WATERFOUL"),
            Edge("AQUATIC_WATERFOUL", "AQUATIC_WADDLE"),
            Edge("MIGRATION_WADDLE", "AQUATIC_WADDLE"),
            Edge("AQUATIC_WADDLE", "BOTTOM_LEFT"),
            Edge("BOTTOM_LEFT", "AQUATIC_WADDLE"),
            Edge("BOTTOM_LEFT", "MIGRATION_QUACK"),
            Edge("MIGRATION_QUACK", "BOTTOM_LEFT"),
            Edge("MIGRATION_WADDLE", "MIGRATION_QUACK"),
            Edge("MIGRATION_QUACK", "MIGRATION_WADDLE"),
            Edge("PONDSIDE_QUACK", "MIGRATION_QUACK"),
            Edge("MIGRATION_QUACK", "PONDSIDE_QUACK"),
            Edge("PONDSIDE_QUACK", "TOP_LEFT"),
            Edge("TOP_LEFT", "PONDSIDE_QUACK"),
            Edge("PONDSIDE_QUACK", "PONDSIDE_WADDLE"),
            Edge("PONDSIDE_WADDLE", "PONDSIDE_QUACK"),
            Edge("BREADCRUMB_WADDLE", "TOP_LEFT"),
            Edge("TOP_LEFT", "BREADCRUMB_WADDLE"),
            Edge("BREADCRUMB_WADDLE", "PONDSIDE_WADDLE"),
            Edge("BREADCRUMB_WADDLE", "BREADCRUMB_CIRCLE"),
            Edge("BREADCRUMB_CIRCLE", "BREADCRUMB_WADDLE"),
            Edge("TAIL_CIRCLE", "BREADCRUMB_CIRCLE"),
            Edge("TAIL_CIRCLE", "TAIL_BEAK"),
            Edge("TAIL_BEAK", "TAIL_CIRCLE"),
            Edge("DABBLER_CIRCLE", "TAIL_CIRCLE"),
            Edge("DABBLER_BEAK", "DABBLER_CIRCLE"),
            Edge("CIRCLE_FEATHER", "DABBLER_CIRCLE"),
            Edge("CIRCLE_FEATHER", "PONDSIDE_FEATHER"),
            Edge("PONDSIDE_FEATHER", "CIRCLE_FEATHER"),
            Edge("CIRCLE_WATERFOUL", "CIRCLE_FEATHER"),
            Edge("PONDSIDE_WATERFOUL", "CIRCLE_WATERFOUL"),
            Edge("PONDSIDE_WATERFOUL", "PONDSIDE_WADDLE"),
            Edge("PONDSIDE_WADDLE", "PONDSIDE_WATERFOUL"),
            Edge("PONDSIDE_WADDLE", "MIGRATION_WADDLE"),
            Edge("MIGRATION_WADDLE", "MIGRATION_WATERFOUL"),
            Edge("MIGRATION_WATERFOUL", "MIGRATION_WADDLE"),
            Edge("AQUATIC_WATERFOUL", "MIGRATION_WATERFOUL"),
            Edge("MIGRATION_FEATHER", "MIGRATION_WATERFOUL"),
            Edge("MIGRATION_WATERFOUL", "MIGRATION_FEATHER"),
            Edge("MIGRATION_WATERFOUL", "PONDSIDE_WATERFOUL"),
            Edge("PONDSIDE_WATERFOUL", "PONDSIDE_FEATHER"),
            Edge("PONDSIDE_FEATHER", "PONDSIDE_WATERFOUL"),
            Edge("MIGRATION_FEATHER", "PONDSIDE_FEATHER"),
            Edge("PONDSIDE_FEATHER", "MIGRATION_FEATHER"),
            Edge("PONDSIDE_BEAK", "PONDSIDE_FEATHER"),
            Edge("PONDSIDE_FEATHER", "PONDSIDE_BEAK"),
            Edge("PONDSIDE_BEAK", "MIGRATION_BEAK"),
            Edge("MIGRATION_BEAK", "PONDSIDE_BEAK"),
            Edge("PONDSIDE_BEAK", "DABBLER_BEAK"),
            Edge("DABBLER_BEAK", "PONDSIDE_BEAK"),
            Edge("PONDSIDE_BEAK", "PONDSIDE_MALLARD"),
            Edge("PONDSIDE_MALLARD", "PONDSIDE_BEAK"),
            Edge("DABBLER_MALLARD", "PONDSIDE_MALLARD"),
            Edge("PONDSIDE_MALLARD", "DABBLER_MALLARD"),
            Edge("MIGRATION_MALLARD", "PONDSIDE_MALLARD"),
            Edge("PONDSIDE_MALLARD", "MIGRATION_MALLARD"),
            Edge("MIGRATION_MALLARD", "BOTTOM_RIGHT"),
            Edge("BOTTOM_RIGHT", "MIGRATION_MALLARD"),
            Edge("MIGRATION_MALLARD", "MIGRATION_BEAK"),
            Edge("MIGRATION_BEAK", "MIGRATION_MALLARD"),
            Edge("AQUATIC_BEAK", "MIGRATION_BEAK"),
            Edge("MIGRATION_BEAK", "AQUATIC_BEAK"),
            Edge("AQUATIC_BEAK", "BOTTOM_RIGHT"),
            Edge("BOTTOM_RIGHT", "AQUATIC_BEAK"),
            Edge("AQUATIC_BEAK", "AQUATIC_FEATHER"),
            Edge("AQUATIC_FEATHER", "AQUATIC_BEAK"),
            Edge("MIGRATION_FEATHER", "AQUATIC_FEATHER"),
            Edge("AQUATIC_FEATHER", "MIGRATION_FEATHER"),
            Edge("AQUATIC_WATERFOUL", "AQUATIC_FEATHER"),
            Edge("AQUATIC_FEATHER", "AQUATIC_WATERFOUL"),
            Edge("DRAKE_BEAK", "DABBLER_BEAK"),
            Edge("DABBLER_BEAK", "DRAKE_BEAK"),
            Edge("DABBLER_MALLARD", "DABBLER_BEAK"),
            Edge("DRAKE_BEAK", "TAIL_BEAK"),
            Edge("TAIL_BEAK", "DRAKE_BEAK"),
            Edge("DRAKE_MALLARD", "DABBLER_MALLARD"),
            Edge("DABBLER_MALLARD", "DUCKLING_MALLARD"),
            Edge("DUCKLING_MALLARD", "TOP_RIGHT"),
            Edge("TOP_RIGHT", "TAIL_BEAK"),
            Edge("DRAKE_BEAK", "DRAKE_MALLARD"),
            Edge("BREADCRUMB_CIRCLE", "CIRCLE_WATERFOUL"),
        ]

    def _build_adjacency(self) -> Dict[str, Dict[str, float]]:
        adjacency: Dict[str, Dict[str, float]] = {name: {} for name in self.nodes}
        for edge in self.edges:
            adjacency[edge.start][edge.end] = self.edge_length(edge)
        return adjacency

    def _build_spawn_points(self) -> Dict[str, SpawnPoint]:
        return {
            "P1": SpawnPoint(
                "P1", Point(170, 19), Edge("AQUATIC_WADDLE", "AQUATIC_WATERFOUL")
            ),
            "P2": SpawnPoint(
                "P2", Point(260, 19), Edge("AQUATIC_WATERFOUL", "AQUATIC_FEATHER")
            ),
            "P3": SpawnPoint(
                "P3", Point(380, 19), Edge("AQUATIC_FEATHER", "AQUATIC_BEAK")
            ),
            "P4": SpawnPoint(
                "P4", Point(515, 19), Edge("BOTTOM_RIGHT", "AQUATIC_BEAK")
            ),
            "P5": SpawnPoint(
                "P5", Point(585, 90), Edge("MIGRATION_MALLARD", "BOTTOM_RIGHT")
            ),
            "P6": SpawnPoint(
                "P6", Point(380, 122), Edge("MIGRATION_FEATHER", "MIGRATION_BEAK")
            ),
            "P7": SpawnPoint(
                "P7", Point(255, 122), Edge("MIGRATION_WATERFOUL", "MIGRATION_FEATHER")
            ),
            "P8": SpawnPoint(
                "P8", Point(170, 122), Edge("MIGRATION_WADDLE", "MIGRATION_WATERFOUL")
            ),
            "P9": SpawnPoint(
                "P9", Point(80, 122), Edge("MIGRATION_QUACK", "MIGRATION_WADDLE")
            ),
            "P10": SpawnPoint(
                "P10", Point(28, 218), Edge("MIGRATION_QUACK", "PONDSIDE_QUACK")
            ),
            "P11": SpawnPoint(
                "P11", Point(585, 178), Edge("MIGRATION_MALLARD", "PONDSIDE_MALLARD")
            ),
            "P12": SpawnPoint(
                "P12", Point(510, 223), Edge("PONDSIDE_BEAK", "PONDSIDE_MALLARD")
            ),
            "P13": SpawnPoint(
                "P13", Point(303, 175), Edge("MIGRATION_FEATHER", "PONDSIDE_FEATHER")
            ),
            "P14": SpawnPoint(
                "P14", Point(184, 242), Edge("PONDSIDE_WADDLE", "PONDSIDE_WATERFOUL")
            ),
            "P15": SpawnPoint(
                "P15", Point(178, 317), Edge("PONDSIDE_WADDLE", "BREADCRUMB_WADDLE")
            ),
            "P16": SpawnPoint(
                "P16", Point(135, 196), Edge("MIGRATION_WADDLE", "PONDSIDE_WADDLE")
            ),
            "P17": SpawnPoint(
                "P17", Point(585, 325), Edge("DABBLER_MALLARD", "DRAKE_MALLARD")
            ),
            "P18": SpawnPoint(
                "P18", Point(510, 283), Edge("DABBLER_BEAK", "DABBLER_MALLARD")
            ),
            "P19": SpawnPoint(
                "P19", Point(576, 455), Edge("TOP_RIGHT", "DUCKLING_MALLARD")
            ),
            "P20": SpawnPoint(
                "P20", Point(525, 392), Edge("DRAKE_BEAK", "DRAKE_MALLARD")
            ),
            "P21": SpawnPoint(
                "P21", Point(452, 360), Edge("DABBLER_BEAK", "DRAKE_BEAK")
            ),
            "P22": SpawnPoint("P22", Point(387, 435), Edge("TAIL_BEAK", "TAIL_CIRCLE")),
            "P23": SpawnPoint(
                "P23", Point(28, 400), Edge("TOP_LEFT", "PONDSIDE_QUACK")
            ),
        }

    def get_node(self, name: str) -> Point:
        return self.nodes[name]

    def get_nodes(self) -> Dict[str, Point]:
        return self.nodes

    def get_edges(self) -> List[Edge]:
        return self.edges

    def get_neighbors(self, node_name: str) -> Dict[str, float]:
        return self.adjacency[node_name]

    def get_spawn_point(self, label: str) -> SpawnPoint:
        return self.spawn_points[label]

    def edge_length(self, edge: Edge) -> float:
        start = self.nodes[edge.start]
        end = self.nodes[edge.end]
        return hypot(end.x - start.x, end.y - start.y)

    def edge_angle(self, edge: Edge) -> int:
        """
        Returns the direction angle of the edge in degrees.

        Convention:
            +X (east)  =   0
            +Y (north) =  90
            -X (west)  = 180
            -Y (south) = 270
        """
        start = self.nodes[edge.start]
        end = self.nodes[edge.end]

        dx = end.x - start.x
        dy = end.y - start.y

        return int(round(degrees(atan2(dy, dx)) % 360))

    def edge_angle_from_nodes(self, start: str, end: str) -> int:
        return self.edge_angle(Edge(start, end))

    def spawn_point_angle(self, label: str) -> int:
        spawn = self.spawn_points[label]
        return self.edge_angle(spawn.edge)

    def project_point_to_edge(self, point: Point, edge: Edge) -> ProjectionResult:
        start = self.nodes[edge.start]
        end = self.nodes[edge.end]

        ax, ay = start.x, start.y
        bx, by = end.x, end.y
        px, py = point.x, point.y

        abx = bx - ax
        aby = by - ay
        apx = px - ax
        apy = py - ay

        ab_len_sq = abx * abx + aby * aby

        if ab_len_sq == 0:
            projected = start
        else:
            t = (apx * abx + apy * aby) / ab_len_sq
            t = max(0.0, min(1.0, t))
            projected = Point(ax + t * abx, ay + t * aby)

        distance_to_edge = hypot(point.x - projected.x, point.y - projected.y)
        distance_from_start = hypot(projected.x - start.x, projected.y - start.y)
        distance_to_end = hypot(end.x - projected.x, end.y - projected.y)

        return ProjectionResult(
            edge=edge,
            projected_point=projected,
            distance_to_edge=distance_to_edge,
            distance_from_start=distance_from_start,
            distance_to_end=distance_to_end,
        )

    def find_closest_edge(self, point: Point) -> ProjectionResult:
        best_result = None

        for edge in self.edges:
            result = self.project_point_to_edge(point, edge)
            if (
                best_result is None
                or result.distance_to_edge < best_result.distance_to_edge
            ):
                best_result = result

        return best_result

