from picarx import Picarx
import time
from typing import Any, Dict, Optional

from safety_module.emergency_stop import detect_emergency_stop, is_emergency_stop
from safety_module.ultrasonic import detect_front_obstacle, can_move_ultrasonic
from safety_module.vision_actions import can_move_vision, detect_visible_danger
import yellow_flag
from safety_module.launch_camera import launch_camera, stop_camera
from yellow_flag import is_flag_active

from VPFS import vpfs_fares_current
from optimization.optimization_interface import OptimizationInterface

import LED_Control.light_controls as lights
import sound.sound as sound
from navigation_interface import NavigationInterface
import navigation_objects
from brake_light import BrakeLightMonitor


class MainController:
    def __init__(self):
        self.px = None
        self.navigation: Optional[NavigationInterface] = None
        self.optimization = OptimizationInterface()

        self.navigation_allowed = False

        self.position = None
        self.heading = None

        self.emergency_stop_status = True
        self.ultrasonic_status = True
        self.visible_danger_status = True
        self.fare_status = False

        self.navigation_task: Optional[Dict[str, Any]] = None

    def bind_navigation(self, navigation: NavigationInterface):
        self.navigation = navigation

    def initialize_vehicle(self):
        print("[MAIN] Initializing vehicle...")

        self.px = Picarx()
        self.px.set_cam_tilt_angle(-20)
        self.px.set_cam_pan_angle(10)
        self.px.stop()
        self.px.set_dir_servo_angle(0)

        print("signal left")
        lights.signal_left()
        time.sleep(2)
        lights.signal_off()
        print("signal right")
        lights.signal_right()
        time.sleep(2)
        lights.signal_off()
        print("headlight on")
        lights.head_light_on()
        time.sleep(2)
        lights.head_light_off()
        print("brake light on")
        lights.brake_light_on()
        time.sleep(2)
        lights.brake_light_off()

        launch_camera()
        print("[MAIN] Camera activated")

        detect_emergency_stop(self.px)
        print("[MAIN] Emergency stop detection started")

        detect_front_obstacle(self.px)
        print("[MAIN] Ultrasonic monitor started")

        yellow_flag.detect_yellow_flag(self.px)
        print("[MAIN] Yellow flag detection started")

        detect_visible_danger()
        print("[MAIN] Visible danger detection started")
        
        self.brake_monitor = BrakeLightMonitor(self)
        self.brake_monitor.start()

        self.navigation_allowed = False
        print("[MAIN] Navigation: DENIED")
        print("[MAIN] Initialization complete\n")

    def _extract_current_fare(self):
        try:
            curr = vpfs_fares_current()
            if curr is None:
                return None

            if isinstance(curr, list) and len(curr) > 0:
                item = curr[0]
                if isinstance(item, dict):
                    return item.get("fare")

            if isinstance(curr, dict):
                return curr.get("fare")

            return None
        except Exception as e:
            print(f"[MAIN] Failed to read current fare: {e}")
            return None

    def _has_active_vpfs_fare(self) -> bool:
        fare = self._extract_current_fare()
        if not fare:
            return False

        if not isinstance(fare, dict):
            return False

        if fare.get("completed", False):
            return False

        if fare.get("paid", False):
            return False

        if fare.get("active", True) is False:
            return False

        return True

    def sync_fare_state(self):
        if self.navigation is None:
            self.fare_status = False
            return

        nav_has_task = self.navigation.has_task()
        nav_phase = self.navigation.get_phase()
        vpfs_has_fare = self._has_active_vpfs_fare()

        self.fare_status = nav_has_task or vpfs_has_fare or (self.navigation_task is not None) or (nav_phase != "IDLE")

        if not self.fare_status:
            self.navigation_task = None

        print(
            f"[MAIN] phase={nav_phase}, nav_has_task={nav_has_task}, "
            f"vpfs_has_fare={vpfs_has_fare}, fare_status={self.fare_status}"
        )

    def update_navigation_permission(self):
        self.emergency_stop_status = not is_emergency_stop()
        self.ultrasonic_status = can_move_ultrasonic()
        self.visible_danger_status = can_move_vision()
        self.sync_fare_state()

        yellow_flag_active = is_flag_active()

        self.navigation_allowed = (
            self.emergency_stop_status
            and self.ultrasonic_status
            and self.visible_danger_status
            and self.fare_status
            and not yellow_flag_active
        )

        navigation_objects.get_status(self.navigation_allowed)

    def request_new_fare(self) -> Optional[Dict[str, Any]]:
        print("[MAIN] Attempting fare request...")
        try:
            data = self.optimization.request_fare()
        except Exception as e:
            print(f"[MAIN] Fare request failed: {e}")
            return None

        if data is None:
            print("[MAIN] No fare claimed")
            return None

        self.navigation_task = data
        self.fare_status = True
        print(f"[MAIN] Fare claimed: {data.get('fare_id')}")
        return data

    def dispatch_claimed_fare(self) -> bool:
        if self.navigation is None:
            print("[MAIN] Navigation interface not bound")
            return False

        if self.navigation_task is None:
            return False

        if self.navigation.has_task():
            return True

        accepted = self.navigation.submit_task(self.navigation_task)
        if accepted:
            self.fare_status = True
            print("[MAIN] Claimed fare sent to navigation")
            return True

        print("[MAIN] submit_task failed")
        return False

    def cleanup(self):
        print("\n[MAIN] Cleaning up before exit...")
        self.navigation_allowed = False

        try:
            if self.px is not None:
                self.px.stop()
                self.px.set_dir_servo_angle(0)
        except Exception as e:
            print(f"[MAIN] Motor cleanup error: {e}")

        try:
            lights.signal_off()
        except Exception as e:
            print(f"[MAIN] Signal light cleanup error: {e}")

        try:
            lights.head_light_off()
        except Exception as e:
            print(f"[MAIN] Head light cleanup error: {e}")

        try:
            lights.brake_light_off()
        except Exception as e:
            print(f"[MAIN] Brake light cleanup error: {e}")

        try:
            sound.stop_sound()
        except Exception as e:
            print(f"[MAIN] Sound cleanup error: {e}")

        try:
            stop_camera()
        except Exception as e:
            print(f"[MAIN] Camera cleanup error: {e}")

        print("[MAIN] Vehicle stopped, lights off, sound off")

    def run(self):
        if self.navigation is None:
            raise RuntimeError("NavigationInterface is not bound to MainController")

        print("[MAIN] Entering main loop")
        try:
            while True:
                self.update_navigation_permission()

                if self.navigation_task is not None and not self.navigation.has_task():
                    self.dispatch_claimed_fare()

                elif (
                    self.navigation_task is None
                    and not self.navigation.has_task()
                    and self.navigation.get_phase() == "IDLE"
                    and not self._has_active_vpfs_fare()
                ):
                    data = self.request_new_fare()
                    if data is not None:
                        self.dispatch_claimed_fare()

                if not can_move_ultrasonic():
                    sound.play_honk()

                time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n[MAIN] KeyboardInterrupt received")

        finally:
            try:
                self.navigation.stop()
            except Exception as e:
                print(f"[MAIN] Navigation thread stop error: {e}")

            self.cleanup()


if __name__ == "__main__":
    controller = MainController()
    navigation = NavigationInterface(controller)
    controller.bind_navigation(navigation)

    try:
        current_fare = controller._extract_current_fare()

        if current_fare:
            navigation.current_phase = "IDLE"

            try:
                recovered_task = controller.optimization.build_task_from_claimed_fare(current_fare)
                controller.navigation_task = recovered_task
                controller.fare_status = recovered_task is not None

                if recovered_task is not None:
                    print(f"[MAIN] Existing VPFS fare recovered: {current_fare.get('id')}")
                    print("[MAIN] Recovered fare will be dispatched to navigation")
                else:
                    print(f"[MAIN] Existing VPFS fare found but recovery failed: {current_fare.get('id')}")
            except Exception as e:
                controller.navigation_task = None
                controller.fare_status = True
                print(f"[MAIN] Failed to recover existing fare: {e}")
        else:
            controller.fare_status = False
            controller.navigation_task = None
            navigation.current_phase = "IDLE"
            print("[MAIN] No active fare at startup")

        controller.initialize_vehicle()
        navigation.start()
        time.sleep(1)
        controller.run()

    except KeyboardInterrupt:
        print("\n[MAIN] Program interrupted during startup/run")
        try:
            navigation.stop()
        except Exception:
            pass
        controller.cleanup()