import subprocess
import os

_vision_process = None


def launch_camera():
    global _vision_process

    if _vision_process is not None:
        print("[CAMERA] Already running")
        return _vision_process

    print("[CAMERA] Launching vision process...")

    venv_python = "/home/d5user/dev/coral/.venv/bin/python"

    cmd = [
        venv_python,
        "/home/d5user/dev/coral/elec392-coral-starter-kit/projects/object_detector_udp.py",
        "--model", "/home/d5user/dev/elec-392-project-duclair-5/src/Trainned Models/efficientdet-lite-custom-signs.tflite",
        "--labels", "/home/d5user/dev/elec-392-project-duclair-5/src/Trainned Models/custom-signs-labels.txt",
        "--confidence", "0.5"
    ]

    _vision_process = subprocess.Popen(cmd)

    print("[CAMERA] Vision process started\n")
    return _vision_process


def stop_camera():
    global _vision_process

    if _vision_process is not None:
        print("[CAMERA] Stopping vision process...")
        try:
            _vision_process.terminate()
            _vision_process.wait(timeout=2)
        except Exception:
            _vision_process.kill()

        _vision_process = None
        print("[CAMERA] Vision process stopped\n")