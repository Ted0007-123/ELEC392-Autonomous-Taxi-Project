import sys
import tty
import time
import termios
import select
import threading
from sound.sound import play_emergency_stop, stop_sound
from LED_Control.light_controls import brake_light_on, brake_light_off, hazard_light_on, signal_off

_thread = None
_triggered = False
_play_sound = None

_lock = threading.Lock()


def _read_key():
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if not rlist:
        return None
    return sys.stdin.read(1)


def _monitor():
    global _triggered

    while True:
        key = _read_key()

        # SPACE -> red flag
        if key == " " and not _triggered:
            with _lock:
                _triggered = True
                play_emergency_stop()
                brake_light_on()
                hazard_light_on()


            print("\n[EMERGENCY STOP] Space pressed - RED FLAG ON")
            print("[EMERGENCY STOP] Press 'r' to release\n")

            

        # r -> release red flag
        elif key == "r" and _triggered:
            with _lock:
                _triggered = False
                stop_sound()
                brake_light_off()
                signal_off()

            print("\n[EMERGENCY STOP RELEASED] RED FLAG OFF\n")

        time.sleep(0.02)


def detect_emergency_stop(play_sound=None):
    global _thread, _play_sound

    _play_sound = play_sound

    if _thread is None:
        fd = sys.stdin.fileno()
        tty.setcbreak(fd)

        print("[EMERGENCY STOP] Emergency stop armed")
        print("[EMERGENCY STOP] SPACE -> RED FLAG ON")
        print("[EMERGENCY STOP] r     -> RED FLAG OFF\n")

        _thread = threading.Thread(target=_monitor, daemon=True)
        _thread.start()


def is_emergency_stop():
    with _lock:
        return _triggered


def get_emergency_stop_status():
    with _lock:
        return not _triggered