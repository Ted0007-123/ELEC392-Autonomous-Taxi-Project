from time import sleep
import threading
import readchar


try:
    import LED_Control.light_controls as lights
except Exception:
    lights = None


DEFAULT_SPEED = 30
MIN_SPEED = 0
MAX_SPEED = 100

STEER_LEFT = -30
STEER_CENTER = 0
STEER_RIGHT = 30

_controller = None
_thread = None
_running = False

_speed = DEFAULT_SPEED
_steer_angle = STEER_CENTER


def _signal_left():
    try:
        if lights is not None:
            lights.signal_left()
    except:
        pass


def _signal_right():
    try:
        if lights is not None:
            lights.signal_right()
    except:
        pass


def _signal_off():
    try:
        if lights is not None:
            lights.signal_off()
    except:
        pass


def _brake_on():
    try:
        if lights is not None:
            lights.brake_light_on()
    except:
        pass


def _brake_off():
    try:
        if lights is not None:
            lights.brake_light_off()
    except:
        pass


def _show_status():
    if _controller is None:
        return

    print(f"[MANUAL] mode={_controller.mode} speed={_speed} steer={_steer_angle}")


def _stop_vehicle():
    global _steer_angle

    if _controller is None or _controller.px is None:
        return

    try:
        _controller.px.forward(0)
    except:
        pass

    try:
        _controller.px.backward(0)
    except:
        pass

    try:
        _controller.px.stop()
    except:
        pass

    try:
        _controller.px.set_dir_servo_angle(STEER_CENTER)
    except:
        pass

    _steer_angle = STEER_CENTER
    _signal_off()
    _brake_on()


def _set_steering(angle):
    global _steer_angle

    if _controller is None or _controller.px is None:
        return

    _steer_angle = angle
    _controller.px.set_dir_servo_angle(angle)


def _forward():
    if _controller is None or _controller.px is None:
        return

    _brake_off()
    _controller.px.forward(_speed)


def _backward():
    if _controller is None or _controller.px is None:
        return

    _brake_off()
    _controller.px.backward(_speed)


def _toggle_mode():
    if _controller is None:
        return

    if _controller.mode == "MANUAL":
        _controller.mode = "AUTO"
        _stop_vehicle()
        print("[MANUAL] Mode changed -> AUTO")
    else:
        _controller.mode = "MANUAL"
        _stop_vehicle()
        print("[MANUAL] Mode changed -> MANUAL")

    _show_status()


def _manual_key_handler(key):
    global _speed

    if _controller is None or _controller.px is None:
        return

    key = key.lower()

    if key == "w":
        _signal_off()
        _forward()

    elif key == "s":
        _signal_off()
        _backward()

    elif key == "a":
        _set_steering(STEER_LEFT)
        _signal_left()
        _show_status()

    elif key == "d":
        _set_steering(STEER_RIGHT)
        _signal_right()
        _show_status()

    elif key == "c":
        _set_steering(STEER_CENTER)
        _signal_off()
        _show_status()

    elif key == "x":
        _stop_vehicle()
        _show_status()

    elif key == "q":
        _speed = max(MIN_SPEED, _speed - 5)
        _show_status()

    elif key == "e":
        _speed = min(MAX_SPEED, _speed + 5)
        _show_status()

    elif key == "m":
        _toggle_mode()


def _auto_key_handler(key):
    global _speed

    key = key.lower()

    if key == "m":
        _toggle_mode()

    elif key == "q":
        _speed = max(MIN_SPEED, _speed - 5)
        _show_status()

    elif key == "e":
        _speed = min(MAX_SPEED, _speed + 5)
        _show_status()

    elif key == "x":
        _stop_vehicle()
        _show_status()


def _loop():
    while _running:
        key = readchar.readkey()

        if key == readchar.key.CTRL_C:
            print("\n[MANUAL] CTRL+C detected")
            _stop_vehicle()
            break

        if _controller is None:
            continue

        if _controller.mode == "MANUAL":
            _manual_key_handler(key)
        else:
            _auto_key_handler(key)


def start_manual_maneuver(controller):
    global _controller, _thread, _running

    _controller = controller

    if _thread is None:
        _running = True
        _thread = threading.Thread(target=_loop, daemon=True)
        _thread.start()
        _show_status()
        print("[MANUAL] Control armed")
        print("[MANUAL] w/s/a/d/c/x/q/e, m to toggle MANUAL/AUTO")


def stop_manual_maneuver():
    global _running

    _running = False
    _stop_vehicle()