from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from .graph import Point
from .route_calculator import RouteCalculator

C1_PAY = 1.0
C2_REPUTATION = 0.0
C3_DISTANCE = 1.0
C4_TIME = 0.0

NOMINAL_SPEED_MPS = 0.225
EPSILON = 1e-9


class FareSelector:
    def __init__(self, route_calculator: RouteCalculator) -> None:
        self.route_calculator = route_calculator

    def _point_from_dict(self, data: Dict[str, float]) -> Point:
        return Point(float(data["x"]), float(data["y"]))

    def _is_fare_available(
        self,
        fare: Dict[str, Any],
        now: Optional[float] = None,
    ) -> bool:
        if fare.get("claimed", False):
            return False

        expiry = fare.get("expiry")
        if expiry is not None:
            if now is None:
                now = time.time()
            if float(expiry) <= now:
                return False

        return True

    def _min_max_normalize(self, value: float, min_value: float, max_value: float) -> float:
        if abs(max_value - min_value) < EPSILON:
            return 1.0
        return (value - min_value) / (max_value - min_value)

    def _compute_total_distance(
        self,
        current_position: Point,
        fare: Dict[str, Any],
    ) -> float:
        src_point = self._point_from_dict(fare["src"])
        dest_point = self._point_from_dict(fare["dest"])

        distance_to_src = self.route_calculator.shortest_distance(current_position, src_point)
        distance_src_to_dest = self.route_calculator.shortest_distance(src_point, dest_point)

        return distance_to_src + distance_src_to_dest

    def _compute_total_time(self, total_distance: float) -> float:
        return total_distance / NOMINAL_SPEED_MPS

    def prepare_fare_metrics(
        self,
        current_position: Point,
        fares: List[Dict[str, Any]],
        now: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        prepared: List[Dict[str, Any]] = []

        for fare in fares:
            if not self._is_fare_available(fare, now):
                continue

            total_distance = self._compute_total_distance(current_position, fare)
            total_time = self._compute_total_time(total_distance)

            prepared.append(
                {
                    "fare": fare,
                    "id": int(fare["id"]),
                    "pay": float(fare.get("pay", 0.0)),
                    "reputation": float(fare.get("reputation", 0.0)),
                    "total_distance": total_distance,
                    "total_time": total_time,
                }
            )

        return prepared

    def score_prepared_fares(
        self,
        prepared_fares: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not prepared_fares:
            return []

        pay_values = [item["pay"] for item in prepared_fares]
        reputation_values = [item["reputation"] for item in prepared_fares]
        distance_values = [item["total_distance"] for item in prepared_fares]
        time_values = [item["total_time"] for item in prepared_fares]

        min_pay, max_pay = min(pay_values), max(pay_values)
        min_rep, max_rep = min(reputation_values), max(reputation_values)
        min_dist, max_dist = min(distance_values), max(distance_values)
        min_time, max_time = min(time_values), max(time_values)

        scored_fares: List[Dict[str, Any]] = []

        for item in prepared_fares:
            pay_norm = self._min_max_normalize(item["pay"], min_pay, max_pay)
            rep_norm = self._min_max_normalize(item["reputation"], min_rep, max_rep)
            dist_norm = self._min_max_normalize(item["total_distance"], min_dist, max_dist)
            time_norm = self._min_max_normalize(item["total_time"], min_time, max_time)

            reward_score = (C1_PAY * pay_norm) + (C2_REPUTATION * rep_norm)
            cost_score = (C3_DISTANCE * dist_norm) + (C4_TIME * time_norm)
            efficiency = reward_score / (reward_score + cost_score + EPSILON)

            scored_fares.append(
                {
                    **item,
                    "pay_norm": pay_norm,
                    "reputation_norm": rep_norm,
                    "distance_norm": dist_norm,
                    "time_norm": time_norm,
                    "reward_score": reward_score,
                    "cost_score": cost_score,
                    "efficiency": efficiency,
                }
            )

        return sorted(scored_fares, key=lambda item: item["efficiency"], reverse=True)

    def select_best_prepared_fare(
        self,
        prepared_fares: List[Dict[str, Any]],
    ) -> Tuple[int, float]:
        scored_fares = self.score_prepared_fares(prepared_fares)

        if not scored_fares:
            raise ValueError("No available fares to select from.")

        best_fare = scored_fares[0]
        return best_fare["id"], best_fare["efficiency"]

    def select_best_fare(
        self,
        current_position: Point,
        fares: List[Dict[str, Any]],
        now: Optional[float] = None,
    ) -> Tuple[int, float]:
        prepared_fares = self.prepare_fare_metrics(current_position, fares, now)
        return self.select_best_prepared_fare(prepared_fares)