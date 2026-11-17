import cv2
import numpy as np
from pathlib import Path

def region_of_interest(img):
    h, w = img.shape[:2]
    mask = np.zeros_like(img)
    polygon = np.array([[
        (int(0.08*w), h),
        (int(0.42*w), int(0.55*h)),
        (int(0.58*w), int(0.55*h)),
        (int(0.92*w), h)
    ]], dtype=np.int32)
    cv2.fillPoly(mask, polygon, 255)
    return cv2.bitwise_and(img, mask)

def average_lane_lines(lines, w, h):
    left, right = [], []
    if lines is None:
        return None, None
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 == x1:
            continue
        slope = (y2-y1) / (x2-x1)
        intercept = y1 - slope*x1
        if slope < -0.35:
            left.append((slope, intercept))
        elif slope > 0.35:
            right.append((slope, intercept))

    def make_line(params):
        if not params:
            return None
        slope, intercept = np.mean(params, axis=0)
        y1, y2 = h, int(h*0.58)
        x1 = int((y1-intercept)/slope)
        x2 = int((y2-intercept)/slope)
        return (x1, y1, x2, y2)

    return make_line(left), make_line(right)

def detect_lanes(frame):
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    roi = region_of_interest(edges)
    lines = cv2.HoughLinesP(roi, 1, np.pi/180, threshold=35,
                            minLineLength=max(25, int(w*0.05)), maxLineGap=80)
    left, right = average_lane_lines(lines, w, h)
    overlay = frame.copy()
    for ln in (left, right):
        if ln:
            cv2.line(overlay, (ln[0],ln[1]), (ln[2],ln[3]), (0,255,0), 7)
    lane_status = "LANE UNCERTAIN"
    if left and right:
        left_bottom, right_bottom = left[0], right[0]
        lane_center = (left_bottom + right_bottom) / 2
        frame_center = w / 2
        offset = lane_center - frame_center
        if abs(offset) < 0.08*w:
            lane_status = "SAFE"
        elif offset < 0:
            lane_status = "SHIFTED LEFT"
        else:
            lane_status = "SHIFTED RIGHT"
        cv2.line(overlay, (int(lane_center), h), (int(lane_center), int(h*0.58)), (255,255,0), 2)
    return overlay, lane_status

def detect_signal_color(frame):
    # Lightweight traffic-light state estimator.
    # It looks for red/yellow/green pixels in the upper-middle road scene.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w = frame.shape[:2]
    roi = hsv[0:int(0.65*h), int(0.15*w):int(0.85*w)]

    masks = {
        "RED": ((np.array([0,100,100]), np.array([10,255,255])),
                (np.array([170,100,100]), np.array([179,255,255]))),
        "YELLOW": ((np.array([18,100,100]), np.array([38,255,255])),),
        "GREEN": ((np.array([40,70,70]), np.array([90,255,255])),)
    }
    scores = {}
    for name, ranges in masks.items():
        score = 0
        for lo, hi in ranges:
            score += int(cv2.countNonZero(cv2.inRange(roi, lo, hi)))
        scores[name] = score

    best = max(scores, key=scores.get)
    # Avoid calling random road colours a signal.
    if scores[best] < max(30, roi.shape[0]*roi.shape[1]*0.0005):
        return "NOT DETECTED"
    return best

def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError("Could not open the uploaded video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)

    # mp4v is broadly available; browser playback can vary by system.
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"),
                             fps, (width, height))
    frames = 0
    last_signal = "NOT DETECTED"
    last_lane = "LANE UNCERTAIN"

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.resize(frame, (width, height))
        annotated, last_lane = detect_lanes(frame)
        last_signal = detect_signal_color(frame)

        if last_signal == "RED":
            status = "STOP — RED SIGNAL"
        elif last_signal == "YELLOW":
            status = "CAUTION — SLOW DOWN"
        elif last_signal == "GREEN":
            status = "GO"
        elif "SHIFTED" in last_lane:
            status = "LANE DEPARTURE WARNING"
        else:
            status = "MONITOR ROAD"

        cv2.rectangle(annotated, (15,15), (470,135), (20,20,20), -1)
        cv2.putText(annotated, f"Traffic Signal: {last_signal}", (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
        cv2.putText(annotated, f"Lane Status: {last_lane}", (30,82),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
        cv2.putText(annotated, status, (30,116),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0,220,255), 2)

        writer.write(annotated)
        frames += 1

    cap.release()
    writer.release()
    return {"frames": frames, "fps": round(fps, 1), "message": "Video processed successfully."}
