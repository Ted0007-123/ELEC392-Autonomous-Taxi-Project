from robot_hat import PWM


class BrakeLED:
    def __init__(self, pwm_pin, brightness=100, pwm_freq=1000):
        self.led = PWM(pwm_pin)
        self.led.freq(pwm_freq)
        self.brightness = brightness
        self._is_on = False

        self.led.pulse_width_percent(0)

    def brake_on(self):
        self.led.pulse_width_percent(self.brightness)
        self._is_on = True

    def brake_off(self):
        self.led.pulse_width_percent(0)
        self._is_on = False

    def brake_is_on(self):
        return self._is_on