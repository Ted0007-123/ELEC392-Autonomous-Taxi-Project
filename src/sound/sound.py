import os
from os import geteuid
from robot_hat import Music

if geteuid() != 0:
    print("\033[0;33mThe program may need to be run with sudo for sound output.\033[0m")

music = Music()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PICKUP_DROPOFF_PATH = os.path.join(SCRIPT_DIR, "pickup_dropoff.mp3")
HONK_PATH = os.path.join(SCRIPT_DIR, "honk.wav")
EMERGENCY_PATH = os.path.join(SCRIPT_DIR, "emergency.mp3")

music.music_set_volume(80)


def play_pickup_dropoff():
    music.sound_play_threading(PICKUP_DROPOFF_PATH)


def play_honk():
    music.sound_play_threading(HONK_PATH)

def play_emergency_stop():
    music.sound_play_threading(EMERGENCY_PATH)


def stop_sound():
    music.music_stop()