import sys
import tty
import time
import termios
import select

from picarx import Picarx
from safety_module.emergency_stop import detect_emergency_stop, can_move
from sound.sound import play_honk, play_pickup_dropoff, play_emergency_stop, stop_sound


def read_key():
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if not rlist:
        return None
    return sys.stdin.read(1)


def main():
    px = Picarx()

    pickup_playing = False

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    detect_emergency_stop(px, play_emergency_stop)

    print("=== test_emergency.py ===")
    print("h     -> play horn")
    print("p     -> toggle pickup/dropoff sound")
    print("SPACE -> emergency stop")
    print("r     -> release emergency stop")
    print("q     -> quit")
    print()

    try:
        while True:
            key = read_key()

            if key == "q":
                break

            if key is None:
                continue

            # emergency stop 상태에서는 일반 입력 막기
            if not can_move():
                if key in ("h", "p"):
                    print("[BLOCKED] Emergency stop is active")
                continue

            if key == "h":
                print("[TEST] Horn")
                play_honk()

            elif key == "p":
                if not pickup_playing:
                    print("[TEST] Pickup/Dropoff sound ON")
                    play_pickup_dropoff()
                    pickup_playing = True
                else:
                    print("[TEST] Pickup/Dropoff sound OFF")
                    stop_sound()
                    pickup_playing = False


    finally:
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

        stop_sound()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nExited test_emergency.py")


if __name__ == "__main__":
    main()