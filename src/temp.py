import threading
import time
import LED_Control.light_controls as lights
# import LineFollower_test


class NavigationTest:
    def __init__(self, controller, speed=20):
        self.controller = controller
        self.px = controller.px
        self.speed = speed
        self.running = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        print("[NAV] navigation test started")

        while self.running:

            print(self.controller.navigation_allowed)
            if self.controller.navigation_allowed:
                lights.brake_light_off()
                self.px.set_dir_servo_angle(0)
                self.px.forward(self.speed)
                #LineFollower_test.Follow_Line()
            else:
                self.px.stop()
                lights.brake_light_on()
            time.sleep(0.05)


    def stop(self):
        self.running = False
        self.px.stop()