import json
import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5005
MIN_SCORE = 0.5
TIMEOUT_CLEAR_SECONDS = 0.75
STOP_HOLD_SECONDS = 1.25   # keep stop sign active briefly after last detection

_thread = None

_visible_danger = False   # 🔴 HARD STOP
_yellow_flag = False      # 🟡 SLOW DOWN

_reason = "not started"
_last_packet_time = 0.0
_last_stop_seen_time = 0.0

_lock = threading.Lock()


def _monitor():
    global _visible_danger, _yellow_flag, _reason, _last_packet_time, _last_stop_seen_time

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.25)

    while True:
        try:
            raw, _ = sock.recvfrom(65535)
            now = time.time()
            _last_packet_time = now

            payload = json.loads(raw.decode())
            detections = payload.get("detections", payload if isinstance(payload, list) else [])

            visible_danger = False
            yellow_flag = False
            reason = "no danger"

            for det in detections:
                score = float(det.get("score", 0.0))
                if score < MIN_SCORE:
                    continue

                label = str(det.get("label", "")).lower()
                bbox = det.get("bbox", [0, 0, 0, 0])

                xmin, ymin, xmax, ymax = bbox
                area = max(0, (xmax - xmin)) * max(0, (ymax - ymin))

                # 🟡 STOP SIGN -> SLOW ONLY
                # Do NOT use the 0.02 area threshold unless bbox is normalized.
                if "stop" in label:
                    _last_stop_seen_time = now
                    yellow_flag = True
                    if not visible_danger:
                        reason = "STOP SIGN AHEAD"
                    print(f"[VISION STOP SIGN] score={score:.2f} bbox={bbox}")

                # 🔴 HARD STOPS
                elif "wheel" in label:
                    if area > 5000:   # example pixel threshold; tune as needed
                        visible_danger = True
                        reason = "CAR WHEELS CLOSE"

                elif "yellow" in label:
                    if area > 12000:  # example pixel threshold; tune as needed
                        visible_danger = True
                        reason = "STOP LINE"

            # hold stop sign briefly even if a frame misses it
            if not yellow_flag and (now - _last_stop_seen_time) <= STOP_HOLD_SECONDS:
                yellow_flag = True
                if not visible_danger:
                    reason = "STOP SIGN AHEAD (held)"

            with _lock:
                _visible_danger = visible_danger
                _yellow_flag = yellow_flag
                _reason = reason

            if visible_danger:
                print(f"[VISION STOP] {reason}")
            elif yellow_flag:
                print(f"[VISION SLOW] {reason}")

        except socket.timeout:
            now = time.time()
            if now - _last_packet_time > TIMEOUT_CLEAR_SECONDS:
                hold_stop = (now - _last_stop_seen_time) <= STOP_HOLD_SECONDS
                with _lock:
                    _visible_danger = False
                    _yellow_flag = hold_stop
                    _reason = "STOP SIGN AHEAD (held)" if hold_stop else "timeout"

        except Exception as e:
            print(f"[VISION ERROR] {e}")
            time.sleep(0.05)


def detect_visible_danger():
    global _thread

    if _thread is None:
        _thread = threading.Thread(target=_monitor, daemon=True)
        _thread.start()

        print("Vision monitor armed")
        print(f"UDP = {HOST}:{PORT}\n")


def can_move_vision():
    with _lock:
        return not _visible_danger


def is_visible_danger():
    with _lock:
        return _visible_danger


def is_yellow_flag():
    with _lock:
        return _yellow_flag


def get_vision_reason():
    with _lock:
        return _reason