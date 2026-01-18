from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import subprocess
import sys
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model globally
model = YOLO("best.pt")

# Global list for detections
detections = []

def generate_frames(mode='processed'):
    global detections
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DSHOW backend
    if not cap.isOpened():
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if mode == 'processed':
            # Run YOLO detection
            results = model.predict(source=frame, imgsz=640, conf=0.6, iou=0.5, device='cpu', verbose=False)
            annotated_frame = results[0].plot()
            # Collect detections
            timestamp = time.time()
            for result in results:
                if result.boxes:
                    for box in result.boxes:
                        cls = int(box.cls)
                        conf = box.conf.item()
                        class_name = model.names[cls]
                        detections.append({
                            'label': class_name,
                            'confidence': conf,
                            'timestamp': timestamp
                        })
            # Keep only last 50 detections
            detections = detections[-50:]
        else:
            annotated_frame = frame  # Raw frame
        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    mode = request.args.get('mode', 'processed')
    return Response(generate_frames(mode), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_detections')
def get_detections():
    global detections
    return jsonify(detections)

def generate_file_frames(file_path):
    global detections
    cap = cv2.VideoCapture(file_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Run YOLO detection
        results = model.predict(source=frame, imgsz=640, conf=0.6, iou=0.5, device='cpu', verbose=False)
        annotated_frame = results[0].plot()
        # Collect detections
        timestamp = time.time()
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    cls = int(box.cls)
                    conf = box.conf.item()
                    class_name = model.names[cls]
                    detections.append({
                        'label': class_name,
                        'confidence': conf,
                        'timestamp': timestamp
                    })
        # Keep only last 50 detections
        detections = detections[-50:]
        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # Add delay to match video fps
        time.sleep(0.03)  # ~30 fps
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
    data = request.json
    mode = data.get('mode')  # 'camera' or 'file'
    file_path = data.get('file_path', 'test_video3.mp4')

    if mode == 'camera':
        # Run final.py with choice 2 (webcam)
        process = subprocess.Popen([sys.executable, 'final.py', '2'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return jsonify({'status': 'running', 'output': stdout, 'error': stderr})
    elif mode == 'file':
        # Run final.py with choice 1 (video file)
        process = subprocess.Popen([sys.executable, 'final.py', '1', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return jsonify({'status': 'running', 'output': stdout, 'error': stderr})
    else:
        return jsonify({'error': 'Invalid mode'}), 400

if __name__ == '__main__':
    app.run(debug=True)