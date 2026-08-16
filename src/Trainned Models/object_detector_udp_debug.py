#!/usr/bin/env python3

import argparse
import socket
import json
import cv2
from pycoral.adapters import common, detect
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file

UDP_IP = "127.0.0.1"
UDP_PORT = 5005


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--confidence", type=float, default=0.5)
    args = parser.parse_args()

    labels = read_label_file(args.labels)

    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    input_w, input_h = common.input_size(interpreter)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    print("Starting detector. Press Ctrl+C to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue

        frame_h, frame_w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (input_w, input_h))

        common.set_input(interpreter, resized)
        interpreter.invoke()

        objs = detect.get_objects(interpreter, args.confidence)

        detections_out = []

        print("\n--- Frame detections ---")
        if not objs:
            print("No objects detected")

        for obj in objs:
            bbox = obj.bbox

            xmin = int(bbox.xmin * frame_w / input_w)
            xmax = int(bbox.xmax * frame_w / input_w)
            ymin = int(bbox.ymin * frame_h / input_h)
            ymax = int(bbox.ymax * frame_h / input_h)

            box_w = xmax - xmin
            box_h = ymax - ymin
            area = box_w * box_h
            center_x = xmin + box_w // 2
            center_y = ymin + box_h // 2

            label = labels.get(obj.id, str(obj.id))
            confidence = float(obj.score)

            print(
                f"label={label:12s} "
                f"conf={confidence:.3f} "
                f"bbox=({xmin},{ymin})-({xmax},{ymax}) "
                f"w={box_w} h={box_h} area={area} "
                f"center=({center_x},{center_y})"
            )

            detections_out.append({
                "label": label,
                "confidence": confidence,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "width": box_w,
                "height": box_h,
                "area": area,
                "center_x": center_x,
                "center_y": center_y,
            })

        sock.sendto(json.dumps(detections_out).encode("utf-8"), (UDP_IP, UDP_PORT))


if __name__ == "__main__":
    main()