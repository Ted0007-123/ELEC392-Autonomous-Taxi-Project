import threading
import time
from typing import Dict, Any, Optional

from CONTROL_TOOLS_EXT import Ackermann_Kinomatic
from Handling_Navagation import NavigationHandle
from optimization.graph import MapGraph
from sound.sound import play_pickup_dropoff
from VPFS import vpfs_whereami, vpfs_fares_current
import LED_Control.light_controls as lights

class NavigationInterface:
    def __init__(self, controller):
        self.controller = controller
        self.graph = MapGraph()

        self.thread = None
        self.running = False

        self.current_phase = "IDLE"
        self.current_task = None

        self.current_handle = None
        self.current_car = 1

        

    def get_phase(self):
        return self.current_phase

    def has_task(self):
        return self.current_task is not None

    def submit_task(self, task):
        if task is None:
            return False

        if self.current_task is not None:
            print("[NAV] Reject task: busy")
            return False

        self.current_task = task
        self.current_phase = "PICKUP"

        print(f"[NAV] Task accepted: {task['fare_id']}")
        return True

    def clear_task(self):
        self._stop_current_handle()

        self.current_task = None
        self.current_phase = "IDLE"
        self.controller.navigation_task = None

        print("[NAV IF] Task cleared -> IDLE")

    def start(self):
        if self.thread is None:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("[NAV IF] Thread started")

    def stop(self):
        self.running = False
        self._stop_current_handle()

    def _stop_vehicle(self):
        try:
            if self.controller.px is not None:
                self.controller.px.forward(0)
        except:
            pass

        try:
            if self.controller.px is not None:
                self.controller.px.backward(0)
        except:
            pass

        try:
            if self.controller.px is not None:
                self.controller.px.stop()
        except:
            pass

    def _stop_current_handle(self):
        if self.current_handle is not None:
            try:
                self.current_handle.stop()
            except Exception as e:
                print(f"[NAV IF] Handle stop error: {e}")

        self.current_handle = None

    def _extract_whereami_position(self):
        data = vpfs_whereami()

        if isinstance(data, list):
            if len(data) == 0:
                return None
            data = data[0]

        pos = data.get("position", {})
        return {
            "x": float(pos.get("x", 0.0)),
            "y": float(pos.get("y", 0.0)),
            "heading": float(pos.get("heading", 0.0)),
        }

    def _build_car_model(self):
        pos = self._extract_whereami_position()
        if pos is None:
            return None

        state = [pos["x"], pos["y"], pos["heading"]]
        input_state = [0, 0]

        return Ackermann_Kinomatic(
            self.controller.px,
            state,
            input_state
        )

    def _node_names_to_points(self, node_names):
        points = []

        for node_name in node_names:
            try:
                node = self.graph.get_node(node_name)
                points.append([node.x, node.y])
            except Exception as e:
                print(f"[NAV IF] Failed to convert node {node_name}: {e}")

        return points

    def _start_handle_for_path(self, node_path):
        self._stop_current_handle()

        points = self._node_names_to_points(node_path)
        if not points:
            print("[NAV IF] Empty point list")
            return False

        car_model = self._build_car_model()
        if car_model is None:
            print("[NAV IF] Failed to build car model from VPFS")
            return False

        self.current_car = car_model
        self.current_handle = NavigationHandle(
            self.controller,
            self.current_car,
            points,
            self.current_phase
        )

        self.current_handle.start()

        print(f"[NAV IF] NavigationHandle started for points: {points}")
        return True

    
    def _get_current_fare_info(self):
        try:
            data = vpfs_fares_current()

            if isinstance(data, list):
                if len(data) == 0:
                    return None
                data = data[0]

            fare = data.get("fare")
            return fare

        except Exception as e:
            print(f"[NAV IF] vpfs_fares_current error: {e}")
            return None

    def _wait_with_vehicle_stopped(self, seconds):
        start_time = time.time()

        while self.running and (time.time() - start_time < seconds):
            self._stop_vehicle()
            time.sleep(0.05)

    def _run_pickup_phase(self):
        pickup_path = self.current_task.get("path_to_pickup", [])
        if not pickup_path:
            print("[NAV IF] Pickup path empty")
            self.current_phase = "ENROUTE"
            return

        print("[NAV IF] Phase -> PICKUP")

        if not self._start_handle_for_path(pickup_path):
            return

        while self.running and self.current_phase == "PICKUP":
            fare = self._get_current_fare_info()

            if fare is None:
                time.sleep(0.1)
                continue

            if fare.get("pickedUp", False):
                print("[NAV IF] Pickup confirmed by VPFS")

                self._stop_current_handle()
                self._stop_vehicle()

                play_pickup_dropoff()
                lights.hazard_light_on()
                self._wait_with_vehicle_stopped(5)
                lights.signal_off()

                self.current_phase = "ENROUTE"
                return

            time.sleep(0.1)

    def _run_enroute_phase(self):
        dropoff_path = self.current_task.get("path_to_destination", [])
        if not dropoff_path:
            print("[NAV IF] Dropoff path empty")
            self.clear_task()
            return

        print("[NAV IF] Phase -> ENROUTE")

        if not self._start_handle_for_path(dropoff_path):
            return

        while self.running and self.current_phase == "ENROUTE":
            fare = self._get_current_fare_info()

            if fare is None:
                time.sleep(0.1)
                continue

            if fare.get("completed", False):
                print("[NAV IF] Dropoff confirmed by VPFS")

                self._stop_current_handle()
                self._stop_vehicle()

                play_pickup_dropoff()
                lights.hazard_light_on()
                self._wait_with_vehicle_stopped(5)
                lights.signal_off()

                self.clear_task()
                return

            time.sleep(0.1)

    def _loop(self):
        while self.running:
            if self.current_task is None:
                self.current_phase = "IDLE"
                time.sleep(0.05)
                continue

            if self.current_phase == "PICKUP":
                self._run_pickup_phase()

            elif self.current_phase == "ENROUTE":
                self._run_enroute_phase()

            else:
                self.current_phase = "IDLE"
                time.sleep(0.05)
