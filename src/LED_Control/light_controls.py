import time
from .flash_LED import BlinkLED
from .brake_LED import BrakeLED

# PWM pin 번호
led_turn_left_front = BlinkLED(9)  # LED 1
led_turn_left_rear = BlinkLED(5)  # LED 2

led_turn_right_front = BlinkLED(7)  # LED 3
led_turn_right_rear = BlinkLED(11)  # LED 4

led_brake_right = BrakeLED(6)  # LED 5
led_brake_left = BrakeLED(8)  # LED 6
led_status = BrakeLED(4)  # LED 7

led_head_left = BrakeLED(9)
led_head_right = BrakeLED(7)


def check_turn_signal(signal1, signal2):
    if signal1._blinking or signal2._blinking:
        signal_off()


def signal_left():
    check_turn_signal(led_turn_left_front, led_turn_left_rear)
    led_turn_left_rear.led_on()
    led_turn_left_front.led_on()


def signal_right():
    check_turn_signal(led_turn_right_front, led_turn_left_front)
    led_turn_right_front.led_on()
    led_turn_right_rear.led_on()


def signal_off():
    led_turn_left_front.led_off()
    led_turn_left_rear.led_off()
    led_turn_right_front.led_off()
    led_turn_right_rear.led_off()
    led_brake_left.brake_off()
    led_brake_right.brake_off
    led_status.brake_off()


def brake_light_on():
    led_brake_right.brake_on()
    led_brake_left.brake_on()


def brake_light_off():
    led_brake_right.brake_off()
    led_brake_left.brake_off()

def head_light_on():
    led_head_left.brake_on()
    led_head_right.brake_on()

def head_light_off():
    led_head_left.brake_off()
    led_head_right.brake_off()

def status_light_on():
    led_status.brake_on()

def status_light_off():
    led_status.brake_off()

def hazard_light_on():
    led_turn_left_rear.led_on()
    led_turn_left_front.led_on()
    led_turn_right_front.led_on()
    led_turn_right_rear.led_on()
