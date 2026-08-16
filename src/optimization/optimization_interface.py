from __future__ import annotations

from typing import Any, Dict, List, Optional

from VPFS import vpfs_fares, vpfs_fares_claim, vpfs_whereami, vpfs_fares_drop, vpfs_fares_current
from optimization.fare_selector import FareSelector
from optimization.graph import MapGraph, Point
from optimization.route_calculator import RouteCalculator


class OptimizationInterface:
    def __init__(self) -> None:
        self.graph = MapGraph()
        self.route_calculator = RouteCalculator(self.graph)
        self.fare_selector = FareSelector(self.route_calculator)
        self.fare_cache: Dict[int, Dict[str, Any]] = {}

    def _get_current_position(self) -> Point:
        data = vpfs_whereami()
        pos = data["position"]
        return Point(float(pos["x"]), float(pos["y"]))

    def _clear_invalid_cache(self, fares: List[Dict[str, Any]]) -> None:
        valid_ids = {int(fare["id"]) for fare in fares}
        cached_ids = list(self.fare_cache.keys())

        for fare_id in cached_ids:
            if fare_id not in valid_ids:
                del self.fare_cache[fare_id]

    def _compute_fare_metrics(
        self,
        current_position: Point,
        fare: Dict[str, Any],
    ) -> Dict[str, Any]:
        fare_id = int(fare["id"])

        if fare_id in self.fare_cache:
            return self.fare_cache[fare_id]

        src = Point(float(fare["src"]["x"]), float(fare["src"]["y"]))
        dest = Point(float(fare["dest"]["x"]), float(fare["dest"]["y"]))

        distance_to_pickup = self.route_calculator.shortest_distance(current_position, src)
        distance_to_destination = self.route_calculator.shortest_distance(src, dest)
        total_distance = distance_to_pickup + distance_to_destination
        total_time = self.fare_selector._compute_total_time(total_distance)

        metrics = {
            "fare": fare,
            "id": fare_id,
            "pay": float(fare.get("pay", 0.0)),
            "reputation": float(fare.get("reputation", 0.0)),
            "total_distance": total_distance,
            "total_time": total_time,
        }

        self.fare_cache[fare_id] = metrics
        return metrics

    def _prepare_fares(
        self,
        current_position: Point,
        fares: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        prepared: List[Dict[str, Any]] = []

        for fare in fares:
            if fare.get("claimed", False):
                continue

            metrics = self._compute_fare_metrics(current_position, fare)
            prepared.append(metrics)

        return prepared

    def _build_result(
        self,
        current_position: Point,
        selected_fare: Dict[str, Any],
        efficiency: float,
    ) -> Dict[str, Any]:
        src = Point(float(selected_fare["src"]["x"]), float(selected_fare["src"]["y"]))
        dest = Point(float(selected_fare["dest"]["x"]), float(selected_fare["dest"]["y"]))

        distance_to_pickup, path_to_pickup = self.route_calculator.shortest_path(current_position, src)
        distance_to_destination, path_to_destination = self.route_calculator.shortest_path(src, dest)

        return {
            "fare_id": int(selected_fare["id"]),
            "efficiency": efficiency,
            "pickup_point": {"x": src.x, "y": src.y},
            "destination_point": {"x": dest.x, "y": dest.y},
            "distance_to_pickup": distance_to_pickup,
            "distance_to_destination": distance_to_destination,
            "path_to_pickup": path_to_pickup,
            "path_to_destination": path_to_destination,
        }

    def request_fare(self) -> Optional[Dict[str, Any]]:
        # curr = vpfs_fares_current()
        # x = curr["fare"]["id"]
        # vpfs_fares_drop(x)
        fares = vpfs_fares()
        current_position = self._get_current_position()

        self._clear_invalid_cache(fares)
        prepared_fares = self._prepare_fares(current_position, fares)

        if not prepared_fares:
            return None

        best_id, efficiency = self.fare_selector.select_best_prepared_fare(prepared_fares)
        claim_response = vpfs_fares_claim(best_id)
        print(claim_response)

        if not claim_response.get("success", False):
            return None

        if best_id in self.fare_cache:
            del self.fare_cache[best_id]

        selected_fare = next(
            fare for fare in fares if int(fare["id"]) == int(best_id)
        )

        return self._build_result(current_position, selected_fare, efficiency)
    
    def build_task_from_claimed_fare(self, claimed_fare: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if claimed_fare is None:
            return None

        fare_id = int(claimed_fare["id"])
        current_position = self._get_current_position()

        metrics = self._compute_fare_metrics(current_position, claimed_fare)
        efficiency = 0.0

        if metrics is not None:
            total_distance = float(metrics.get("total_distance", 0.0))
            total_time = float(metrics.get("total_time", 0.0))
            pay = float(metrics.get("pay", 0.0))
            reputation = float(metrics.get("reputation", 0.0))

            prepared = [{
                "fare": claimed_fare,
                "id": fare_id,
                "pay": pay,
                "reputation": reputation,
                "total_distance": total_distance,
                "total_time": total_time,
            }]

            scored = self.fare_selector.score_prepared_fares(prepared)
            if scored:
                efficiency = float(scored[0].get("efficiency", 0.0))

        return self._build_result(current_position, claimed_fare, efficiency)
