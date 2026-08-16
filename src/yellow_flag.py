import time
import threading

import safety_module.vision_actions as va

CHECK_INTERVAL = 0.05
PENALTY_SECONDS = 3.0
YELLOW_THRESHOLD = 1100

_px = None
_thread = None

_yellow_flag_status = False
_red_flag_status = False
_penalty_active = False
_grayscale_values = None

_lock = threading.Lock()


def update_flag_status():
    global _yellow_flag_status
    _yellow_flag_status = va.is_yellow_flag()
    # print(f"STOP SIGN DETECTED {_yellow_flag_status}")
    return


def _all_greyscale_yellow(values):
    if values is None or len(values) != 3:
        return False

    left, mid, right = values
    # print(f"GRAY SCALE LEVEL [{left},{mid}, {right}]")

    return (
        left >= YELLOW_THRESHOLD
        and mid >= YELLOW_THRESHOLD
        and right >= YELLOW_THRESHOLD
    )


def _run_penalty():
    global _penalty_active, _yellow_flag_status, _red_flag_status
    with _lock:
        _red_flag_status = True
        _penalty_active = True
    print("[YELLOW FLAG] penalty start")

    time.sleep(PENALTY_SECONDS)

    with _lock:
        _penalty_active = False
        _yellow_flag_status = False
        _red_flag_status = False

    print("[YELLOW FLAG] penalty end")


def _monitor():
    global _yellow_flag_status, _penalty_active, _grayscale_values

    while True:
        _grayscale_values = _px.get_grayscale_data()
        _all_greyscale_yellow(_grayscale_values)
        update_flag_status()
        if(_yellow_flag_status and not _penalty_active and _all_greyscale_yellow(_grayscale_values)):
            _run_penalty()
        time.sleep(CHECK_INTERVAL)


def detect_yellow_flag(px):
    global _px, _thread

    _px = px

    if _thread is None:
        _thread = threading.Thread(target=_monitor, daemon=True)
        _thread.start()

        print("Yellow flag monitor armed")
        print(f"CHECK_INTERVAL = {CHECK_INTERVAL} sec")
        print(f"PENALTY_SECONDS = {PENALTY_SECONDS} sec")
        print(f"YELLOW_THRESHOLD = {YELLOW_THRESHOLD}\n")


def is_flag_active():
    with _lock:
        return _red_flag_status
    
def yellow_flag_status():
    return _yellow_flag_status