import sys
import tty
import termios
import select
from time import sleep

from picarx import Picarx

from safety_module.emergency_stop import (
    detect_emergency_stop,
    can_move as can_move_emergency,
    is_emergency_stop,
)
from safety_module.ultrasonic import (
    detect_front_obstacle,
    can_move_ultrasonic,
    is_blocked as is_ultrasonic_blocked,
    get_front_distance,
)
from sound.sound import play_emergency_stop

try:
    from LED_Control.light_controls import (
        signal_left,
        signal_right,
        signal_off,
        brake_light_on,
        brake_light_off,
    )
except Exception:
    def signal_left():
        pass

    def signal_right():
        pass

    def signal_off():
        pass

    def brake_light_on():
        pass

    def brake_light_off():
        pass


DEFAULT_SPEED = 30
MIN_SPEED = 0
MAX_SPEED = 100

STEER_LEFT = -30
STEER_CENTER = 0
STEER_RIGHT = 30

LOOP_DELAY = 0.02

mode = "MANUAL"
drive_state = "STOP"
steer_angle = STEER_CENTER
speed = DEFAULT_SPEED
_last_status = ""


def read_key_nonblocking():
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if not rlist:
        return None
    return sys.stdin.read(1)


def stop_vehicle(px):
    try:
        px.forward(0)
    except:
        pass

    try:
        px.backward(0)
    except:
        pass

    try:
        px.stop()
    except:
        pass


def apply_motion(px, drive, steer, speed_value):
    px.set_dir_servo_angle(steer)

    if drive == "FORWARD":
        brake_light_off()
        px.forward(speed_value)

    elif drive == "BACKWARD":
        brake_light_off()
        px.backward(speed_value)

    else:
        stop_vehicle(px)
        brake_light_on()


def status_text():
    lines = []
    lines.append("=== main.py ===")
    lines.append("")
    lines.append("Manual control")
    lines.append("  w : forward request")
    lines.append("  s : backward request")
    lines.append("  a : steer left")
    lines.append("  d : steer right")
    lines.append("  c : steer center")
    lines.append("  x : stop request")
    lines.append("")
    lines.append("System")
    lines.append("  q : speed down")
    lines.append("  e : speed up")
    lines.append("  m : toggle MANUAL / AUTO")
    lines.append("  ctrl+c : exit")
    lines.append("")
    lines.append("Emergency")
    lines.append("  space : emergency stop")
    lines.append("  r     : release emergency stop")
    lines.append("")
    lines.append(f"Mode             : {mode}")
    lines.append(f"Drive state      : {drive_state}")
    lines.append(f"Steer angle      : {steer_angle}")
    lines.append(f"Speed            : {speed}")
    lines.append("")
    lines.append("Safety state")
    lines.append(f"  Emergency OK   : {can_move_emergency()}")
    lines.append(f"  Ultrasonic OK  : {can_move_ultrasonic()}")
    lines.append(f"  Front dist     : {get_front_distance()}")
    lines.append("")

    if is_emergency_stop():
        lines.append("[HARD STOP] Emergency stop is active")
    elif is_ultrasonic_blocked():
        lines.append("[SOFT STOP] Ultrasonic obstacle detected")
    else:
        lines.append("[READY] Motion allowed")

    return "\n".join(lines)


def show_status(force=False):
    global _last_status
    text = status_text()
    if force or text != _last_status:
        print("\033[H\033[J", end="")
        print(text)
        _last_status = text


def update_manual_command(key):
    global drive_state, steer_angle, speed, mode

    if key == 'w':
        drive_state = "FORWARD"

    elif key == 's':
        drive_state = "BACKWARD"

    elif key == 'x':
        drive_state = "STOP"

    elif key == 'a':
        steer_angle = STEER_LEFT
        signal_left()

    elif key == 'd':
        steer_angle = STEER_RIGHT
        signal_right()

    elif key == 'c':
        steer_angle = STEER_CENTER
        signal_off()

    elif key == 'q':
        speed = max(MIN_SPEED, speed - 5)

    elif key == 'e':
        speed = min(MAX_SPEED, speed + 5)

    elif key == 'm':
        drive_state = "STOP"
        mode = "AUTO"


def update_auto_command(key):
    global drive_state, steer_angle, speed, mode

    if key == 'm':
        drive_state = "STOP"
        mode = "MANUAL"

    elif key == 'q':
        speed = max(MIN_SPEED, speed - 5)

    elif key == 'e':
        speed = min(MAX_SPEED, speed + 5)

    elif key == 'x':
        drive_state = "STOP"

    # Auto mode continuously requests forward motion
    steer_angle = STEER_CENTER
    signal_off()
    drive_state = "FORWARD"


def evaluate_permissions():
    if not can_move_emergency():
        return "STOP", "EMERGENCY_STOP"

    # Soft stop only blocks forward motion
    if not can_move_ultrasonic() and drive_state == "FORWARD":
        return "STOP", "ULTRASONIC_BLOCKED"

    return drive_state, None


def main():
    global mode

    px = None
    fd = None
    old_settings = None

    try:
        px = Picarx()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        detect_emergency_stop(px, play_emergency_stop)
        detect_front_obstacle(px)

        show_status(force=True)

        while True:
            key = read_key_nonblocking()

            if key is not None:
                key = key.lower()

                if ord(key) == 3:  # Ctrl+C
                    raise KeyboardInterrupt

                if mode == "MANUAL":
                    update_manual_command(key)
                else:
                    update_auto_command(key)

            else:
                # Keep AUTO mode requesting motion even with no key press
                if mode == "AUTO":
                    update_auto_command(None)

            final_drive, stop_reason = evaluate_permissions()
            apply_motion(px, final_drive, steer_angle, speed)

            if stop_reason is not None:
                brake_light_on()

            show_status()

    except KeyboardInterrupt:
        print("\nQuit")

    finally:
        if px is not None:
            try:
                px.set_dir_servo_angle(STEER_CENTER)
            except:
                pass

            try:
                stop_vehicle(px)
            except:
                pass

            try:
                signal_off()
            except:
                pass

        if fd is not None and old_settings is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)



if __name__ == "__main__":
    main()