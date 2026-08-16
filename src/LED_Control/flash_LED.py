import time
import threading
from robot_hat import PWM


class BlinkLED:
    def __init__(self, pwm_pin, bpm=68, brightness=100, pwm_freq=1000):
        self.led = PWM(pwm_pin)
        self.led.freq(pwm_freq)

        self.brightness = brightness
        self.half_period = 60.0 / bpm / 2.0

        self._blinking = False
        self._thread = None
        self._lock = threading.Lock()

        self.led.pulse_width_percent(0)

    def _worker(self):
        while True:
            with self._lock:
                if not self._blinking:
                    break

            self.led.pulse_width_percent(self.brightness)
            time.sleep(self.half_period)

            with self._lock:
                if not self._blinking:
                    break

            self.led.pulse_width_percent(0)
            time.sleep(self.half_period)

        self.led.pulse_width_percent(0)

    def led_on(self):
        with self._lock:
            if self._blinking:
                return
            self._blinking = True

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def led_off(self):
        with self._lock:
            self._blinking = False
        self.led.pulse_width_percent(0)
