import threading
import time
import LED_Control.light_controls as lights


class BrakeLightMonitor:
    def __init__(self, controller, interval=0.05):
        self.controller = controller
        self.interval = interval
        self.running = False
        self.thread = None

        self._last_state = None  # True = moving

    def start(self):
        if self.thread is None:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            px = self.controller.px

            moving = False

            try:
                # Picarx 내부 motor speed 읽기
                left = px.motor_speed[0]
                right = px.motor_speed[1]

                if abs(left) > 0 or abs(right) > 0:
                    moving = True

            except:
                pass

            # 상태 바뀔 때만 LED 변경
            if moving != self._last_state:
                if moving:
                    lights.brake_light_off()
                else:
                    lights.brake_light_on()

                self._last_state = moving

            time.sleep(self.interval)