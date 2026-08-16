import time
import threading

SAFE_DISTANCE = 30
READ_INTERVAL = 0.05
WINDOW_SIZE = 10

_px = None
_thread = None

_blocked = False
_distance = None
_samples = []

_lock = threading.Lock()


def _monitor():
    global _blocked, _distance, _samples

    while True:
        distance = None

        try:
            if _px is not None:
                distance = _px.ultrasonic.read()
        except:
            distance = None

        with _lock:
            # 유효한 값만 평균 버퍼에 추가
            if distance is not None:
                _samples.append(distance)

                if len(_samples) > WINDOW_SIZE:
                    _samples.pop(0)

            # 최근 유효 샘플 평균 계산
            if len(_samples) == 0:
                _distance = None
                _blocked = True   # fail safe
            else:
                avg_distance = sum(_samples) / len(_samples)
                _distance = avg_distance
                _blocked = avg_distance < SAFE_DISTANCE

        time.sleep(READ_INTERVAL)


def detect_front_obstacle(px):
    global _px, _thread

    _px = px

    if _thread is None:
        _thread = threading.Thread(target=_monitor, daemon=True)
        _thread.start()

        print("Ultrasonic monitor armed")
        print(f"SAFE_DISTANCE = {SAFE_DISTANCE} cm")
        print(f"WINDOW_SIZE = {WINDOW_SIZE}\n")


def can_move_ultrasonic():
    with _lock:
        return not _blocked


def is_blocked():
    with _lock:
        return _blocked


def get_front_distance():
    with _lock:
        return _distance