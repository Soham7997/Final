from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import time
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

import cv2
import torch
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -----------------------------
# Model + tracking configuration
# -----------------------------
model = YOLO("best.pt")
print("[INFO] Model class names:", model.names)

DEVICE = 0 if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {'GPU' if DEVICE == 0 else 'CPU'}")

# Deliverable folders
BASE_SAVE_DIR = "detections"
os.makedirs(BASE_SAVE_DIR, exist_ok=True)

# Change these to match your model.names exactly (case-insensitive compare is used)
TARGET_CLASSES = {"man", "woman", "child"}

for cls in TARGET_CLASSES:
    os.makedirs(os.path.join(BASE_SAVE_DIR, cls), exist_ok=True)

# Per-class counters + mapping (class, track_id) -> Human ID (Man1/Woman2/Child3)
class_counters = {cls: 0 for cls in TARGET_CLASSES}
track_to_human_id = {}

# CSV logging
CSV_PATH = os.path.join(BASE_SAVE_DIR, "tracking_log.csv")
csv_file = open(CSV_PATH, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "timestamp_iso", "source", "frame",
    "class", "human_id", "track_id",
    "conf", "x1", "y1", "x2", "y2",
    "crop_path", "posture_hint", "motion_score", "child_by_scale_hint"
])
print(f"[INFO] Logging to CSV: {CSV_PATH}")

# In-memory rolling detections for UI
detections = []  # keep last N events

# For simple motion score
_prev_gray = None


def _safe_lower_name(cls_id: int) -> str:
    name = model.names.get(int(cls_id), str(cls_id))
    return str(name).strip().lower()


def _get_human_id(class_name: str, track_id: int) -> str:
    key = (class_name, int(track_id))
    if key not in track_to_human_id:
        class_counters[class_name] += 1
        track_to_human_id[key] = f"{class_name.capitalize()}{class_counters[class_name]}"
    return track_to_human_id[key]


def _clamp_box(x1, y1, x2, y2, w, h):
    x1 = max(0, min(int(x1), w - 1))
    x2 = max(0, min(int(x2), w - 1))
    y1 = max(0, min(int(y1), h - 1))
    y2 = max(0, min(int(y2), h - 1))
    return x1, y1, x2, y2


def _posture_hint_from_box(x1, y1, x2, y2):
    # Very basic posture proxy: aspect ratio
    bw = max(1, (x2 - x1))
    bh = max(1, (y2 - y1))
    ar = bh / bw
    if ar > 2.2:
        return "standing/upright"
    if ar < 1.4:
        return "crouched/sitting/unclear"
    return "unknown"


def _motion_score_in_box(prev_gray, gray, x1, y1, x2, y2):
    # Frame-diff based motion score in the bbox (0..255 approx)
    if prev_gray is None:
        return 0.0
    roi_prev = prev_gray[y1:y2, x1:x2]
    roi_now = gray[y1:y2, x1:x2]
    if roi_prev.size == 0 or roi_now.size == 0:
        return 0.0
    diff = cv2.absdiff(roi_prev, roi_now)
    return float(diff.mean())


def _child_by_scale_hint(person_heights, this_height):
    # Context hint only (does not change class): if much smaller than median, likely child
    if not person_heights:
        return False
    person_heights_sorted = sorted(person_heights)
    mid = len(person_heights_sorted) // 2
    median_h = person_heights_sorted[mid]
    return this_height < 0.65 * median_h


def _append_detection(event, max_keep=80):
    global detections
    detections.append(event)
    detections = detections[-max_keep:]


def _run_track_on_frame(frame, source_label, frame_idx):
    """
    Runs YOLOv8 + ByteTrack, saves crops, logs CSV, updates detections list.
    Returns annotated_frame.
    """
    global _prev_gray

    # Track
    results = model.track(
        source=frame,
        imgsz=640,
        conf=0.6,
        iou=0.5,
        device=DEVICE,
        tracker="bytetrack.yaml",
        persist=True,
        verbose=False
    )

    r0 = results[0]
    annotated = r0.plot()

    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if r0.boxes is None or len(r0.boxes) == 0:
        _prev_gray = gray
        return annotated

    xyxy = r0.boxes.xyxy.detach().cpu().numpy()
    cls_ids = r0.boxes.cls.detach().cpu().numpy()
    confs = r0.boxes.conf.detach().cpu().numpy() if getattr(r0.boxes, "conf", None) is not None else None

    track_ids = getattr(r0.boxes, "id", None)
    if track_ids is not None:
        track_ids = track_ids.detach().cpu().numpy()

    # Build person heights for contextual "child_by_scale_hint"
    person_heights = []
    for i, (box, cid) in enumerate(zip(xyxy, cls_ids)):
        cname = _safe_lower_name(cid)
        if cname in TARGET_CLASSES:
            x1, y1, x2, y2 = _clamp_box(*box, w=w, h=h)
            person_heights.append(max(1, y2 - y1))

    timestamp_iso = datetime.now().isoformat(timespec="milliseconds")
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    for i, (box, cid) in enumerate(zip(xyxy, cls_ids)):
        class_name = _safe_lower_name(cid)
        if class_name not in TARGET_CLASSES:
            continue

        x1, y1, x2, y2 = _clamp_box(*box, w=w, h=h)
        if x2 <= x1 or y2 <= y1:
            continue

        conf = float(confs[i]) if confs is not None else None
        tid = int(track_ids[i]) if track_ids is not None else int(i)

        human_id = _get_human_id(class_name, tid)

        # Crop + save
        crop = frame[y1:y2, x1:x2]
        crop_rel = os.path.join(BASE_SAVE_DIR, class_name, f"{timestamp_file}_{human_id}.jpg")
        crop_abs = os.path.abspath(crop_rel)
        cv2.imwrite(crop_rel, crop)

        # Minimal posture/behavior fusion (hint only)
        posture_hint = _posture_hint_from_box(x1, y1, x2, y2)
        motion_score = _motion_score_in_box(_prev_gray, gray, x1, y1, x2, y2)
        child_scale_hint = _child_by_scale_hint(person_heights, (y2 - y1))

        # Overlay ID + conf
        label = f"{human_id}"
        if conf is not None:
            label += f" {conf:.2f}"
        cv2.putText(
            annotated,
            label,
            (x1, max(15, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # CSV
        csv_writer.writerow([
            timestamp_iso, source_label, frame_idx,
            class_name, human_id, tid,
            conf if conf is not None else "",
            x1, y1, x2, y2,
            crop_rel,
            posture_hint,
            f"{motion_score:.2f}",
            int(child_scale_hint)
        ])

        # UI event payload
        event = {
            "timestamp": timestamp_iso,
            "source": source_label,
            "frame": frame_idx,
            "label": class_name,          # for backwards compatibility
            "human_id": human_id,
            "track_id": tid,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2],
            "crop_url": f"/{crop_rel.replace(os.sep, '/')}",
            "posture_hint": posture_hint,
            "motion_score": motion_score,
            "child_by_scale_hint": child_scale_hint
        }
        _append_detection(event)

    _prev_gray = gray
    return annotated


def generate_frames(mode='processed'):
    # preserves your original endpoint behavior
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
        return

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if mode == 'processed':
            annotated_frame = _run_track_on_frame(frame, source_label="camera", frame_idx=frame_idx)
        else:
            annotated_frame = frame

        ok, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ok:
            continue
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        frame_idx += 1


@app.route('/video_feed')
def video_feed():
    mode = request.args.get('mode', 'processed')
    return Response(generate_frames(mode), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_detections')
def get_detections():
    # returns last N events for UI
    return jsonify(detections)


def generate_file_frames(file_path):
    cap = cv2.VideoCapture(file_path)
    frame_idx = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30.0
    delay = 1.0 / fps

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame = _run_track_on_frame(frame, source_label="file", frame_idx=frame_idx)

        ok, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ok:
            continue
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        frame_idx += 1
        time.sleep(delay)

    cap.release()


@app.route('/video_file_feed')
def video_file_feed():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return "File not found", 404
    return Response(generate_file_frames(file_path), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    # This keeps your original behavior AND allows serving crops under /detections/...
    return send_from_directory('.', path)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return jsonify({'file_path': file_path})


@app.route('/run_detection', methods=['POST'])
def run_detection():
    """
    Keep this endpoint for compatibility.
    Instead of subprocess-running final.py, we simply return what the UI needs:
    - for camera: stream from /video_feed
    - for file: upload then stream from /video_file_feed?file_path=...
    """
    data = request.json or {}
    mode = data.get('mode')  # 'camera' or 'file'
    file_path = data.get('file_path')

    if mode == 'camera':
        return jsonify({
            'status': 'ok',
            'stream_url': '/video_feed?mode=processed'
        })

    if mode == 'file':
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Invalid file_path'}), 400
        return jsonify({
            'status': 'ok',
            'stream_url': f'/video_file_feed?file_path={file_path}'
        })

    return jsonify({'error': 'Invalid mode'}), 400


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Ensure CSV closes
        try:
            csv_file.close()
        except Exception:
            pass