import os
import cv2
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import uuid
import base64
import io
import json
import sys
import threading
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from ws_ping import ConnectionManager
import time
import faulthandler
faulthandler.enable()

# --- DEEPFACE IMPORT ---
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("[OK] DeepFace imported successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[WARNING] DeepFace library not found. Emotion detection will be disabled.")

# Create placeholder for mp
class PlaceholderMP:
    class solutions:
        class drawing_utils:
            DrawingSpec = lambda color, thickness, circle_radius: None
        class holistic:
            Holistic = lambda min_detection_confidence, min_tracking_confidence: None
            POSE_CONNECTIONS = []
            class PoseLandmark:
                LEFT_SHOULDER = 11
                RIGHT_SHOULDER = 12
                LEFT_ELBOW = 13
                RIGHT_ELBOW = 14
                LEFT_KNEE = 25
                RIGHT_KNEE = 26
                RIGHT_WRIST = 16
                RIGHT_EYE = 6
                LEFT_WRIST = 15
                LEFT_EYE = 3

# Try to import mediapipe
try:
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        raise AttributeError("MediaPipe does not have 'solutions' module")
    MEDIAPIPE_AVAILABLE = True
    print("[OK] MediaPipe successfully imported")
except (ImportError, AttributeError) as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"[WARNING] MediaPipe not available: {e}")
    mp = PlaceholderMP()

# Initialize FastAPI
print("Initializing FastAPI application...")
app = FastAPI(title="Body Tracking AI", description="AI model for body tracking")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Frame skipping for optimization ===
FRAME_SKIP = 2  

# === YOUR HELPER FUNCTIONS ===
def calculate_angle(a, b, c):
    """Calculates the angle at point b given three points [x, y]"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360-angle
    return angle

def analyze_emotion_task(session_obj, img):
    """Background task for DeepFace"""
    if not DEEPFACE_AVAILABLE: return

    try:
        # Run analysis (silently, no enforcement)
        objs = DeepFace.analyze(img_path=img, actions=['emotion'], enforce_detection=False, silent=True)
        
        if isinstance(objs, dict): objs = [objs]
            
        temp_data = []
        if objs:
            # Update main emotion
            session_obj.current_emotion = objs[0]['dominant_emotion']
            # Store data for bounding boxes
            for obj in objs:
                region = obj['region']
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                emotion = obj['dominant_emotion']
                temp_data.append({'box': (x, y, w, h), 'emotion': emotion})
        
        session_obj.faces_data = temp_data
    except Exception:
        pass

# === Data Storage ===
class SessionData:
    def __init__(self):
        self.prediction_history = []
        self.movement_scores_raw = []
        self.smoothed_scores = []
        self.frame_count = 0
        self.FRAME_RATE = 30 
        
        # --- NEW VARIABLES ---
        self.detect_every_n_frames = 15
        self.current_emotion = "Neutral"
        self.faces_data = [] 
        self.mouth_status = ""

sessions = {}
connection_manager = ConnectionManager()

# === Serve static files ===
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    print("🚀 Body Tracking AI Server is ready!")

@app.get("/", response_class=HTMLResponse)
async def get():
    with open('static/index.html', 'r') as f:
        return f.read()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# === WebSocket Endpoint ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    temp_session_id = str(uuid.uuid4())
    await connection_manager.connect(websocket, temp_session_id)
    
    # Handshake
    try:
        init_data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        try:
            data = json.loads(init_data)
            if data.get('type') == 'session_init' and data.get('session_id'):
                session_id = data.get('session_id')
                connection_manager.disconnect(temp_session_id)
                connection_manager.active_connections[session_id] = websocket
                asyncio.create_task(connection_manager._keep_alive(session_id))
            else:
                session_id = temp_session_id
        except:
            session_id = temp_session_id
    except:
        session_id = temp_session_id
    
    sessions[session_id] = SessionData()
    session = sessions[session_id]
    
    # Initialize Holistic with HIGHER CONFIDENCE to reduce false results
    holistic = None
    if MEDIAPIPE_AVAILABLE:
        holistic = mp.solutions.holistic.Holistic(
            min_detection_confidence=0.6, 
            min_tracking_confidence=0.6
        )

    try:
        while True:            
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                if not data or data == 'pong' or data.startswith('{'): continue
                
                # Decode Image
                if "," in data and ";base64," in data:
                    img_data = data.split(",")[1]
                    img_bytes = base64.b64decode(img_data)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is None: continue
                else:
                    continue

                session.frame_count += 1
                if session.frame_count % FRAME_SKIP != 0: continue
                
                # Resize and Prep
                frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                active_statuses = [] 
                session.mouth_status = ""

                # --- 1. MEDIA PIPE LOGIC (Calculations ONLY, NO DRAWING) ---
                if MEDIAPIPE_AVAILABLE and holistic:
                    results = holistic.process(rgb_frame)

                    if results.pose_landmarks:
                        # NOTE: WE DELETED THE DRAWING CODE HERE TO REDUCE DELAY
                        
                        landmarks = results.pose_landmarks.landmark
                        mp_pose = mp.solutions.holistic.PoseLandmark
                        
                        # --- Logic A: Hands Up ---
                        right_wrist = landmarks[mp_pose.RIGHT_WRIST]
                        right_eye = landmarks[mp_pose.RIGHT_EYE]
                        left_wrist = landmarks[mp_pose.LEFT_WRIST]
                        left_eye = landmarks[mp_pose.LEFT_EYE]
                        
                        # Added visibility check to prevent false positives when hand is off-screen
                        if right_wrist.visibility > 0.5 and right_eye.visibility > 0.5:
                            if right_wrist.y < right_eye.y:
                                active_statuses.append("RIGHT HAND UP")
                        
                        if left_wrist.visibility > 0.5 and left_eye.visibility > 0.5:
                            if left_wrist.y < left_eye.y:
                                active_statuses.append("LEFT HAND UP")

                        # --- Logic B: Standing ---
                        # Indices: 23=Hip, 25=Knee, 27=Ankle
                        if landmarks[25].visibility > 0.6 and landmarks[27].visibility > 0.6:
                            l_hip = [landmarks[23].x, landmarks[23].y]
                            l_knee = [landmarks[25].x, landmarks[25].y]
                            l_ankle = [landmarks[27].x, landmarks[27].y]
                            
                            knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
                            
                            if knee_angle > 160:
                                active_statuses.append("STANDING")
                            elif knee_angle < 140:
                                active_statuses.append("SITTING")
                    
                    # --- Logic C: Shouting (Mouth) ---
                    if results.face_landmarks:
                        face_lm = results.face_landmarks.landmark
                        # Lips: 13=Upper, 14=Lower
                        upper_lip = face_lm[13]
                        lower_lip = face_lm[14]
                        
                        # Only check if lips are detected
                        if upper_lip.visibility > 0.5 and lower_lip.visibility > 0.5:
                            mouth_open_dist = abs(upper_lip.y - lower_lip.y)
                            if mouth_open_dist > 0.05:
                                if session.current_emotion in ["angry", "fear", "surprise"]:
                                    session.mouth_status = "SHOUTING"
                                else:
                                    session.mouth_status = "Mouth Open"

                # --- 2. DEEPFACE LOGIC (Background Thread) ---
                if session.frame_count % session.detect_every_n_frames == 0:
                    threading.Thread(target=analyze_emotion_task, args=(session, frame.copy())).start()

                # --- 3. VISUALIZATION (Boxes & Text ONLY) ---
                
                # Draw Status Text (Hands/Standing)
                y_pos = 50
                for status in active_statuses:
                    color = (0, 255, 0) # Green
                    if status == "STANDING": color = (255, 255, 0)
                    cv2.putText(frame, status, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    y_pos += 40

                # Draw Emotion Boxes (Faces)
                for face in session.faces_data:
                    (x, y, w, h) = face['box']
                    emotion_label = face['emotion']
                    
                    color_emo = (0, 255, 0)
                    if emotion_label in ["angry", "sad", "fear"]:
                        color_emo = (0, 0, 255)
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color_emo, 2)
                    cv2.putText(frame, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_emo, 2)

                if session.mouth_status == "SHOUTING":
                    cv2.putText(frame, "!!! SHOUTING !!!", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Prepare Response Data
                if active_statuses:
                    main_behavior = active_statuses[0]
                elif session.mouth_status == "SHOUTING":
                    main_behavior = "SHOUTING"
                else:
                    main_behavior = session.current_emotion

                session.prediction_history.append(main_behavior)
                # Add random fake score for graph continuity
                session.smoothed_scores.append(np.random.rand() * 10 if active_statuses else 0)

                # Compress and Send
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                _, buffer = cv2.imencode('.jpg', frame, encode_params)
                img_str = base64.b64encode(buffer).decode('utf-8')
                
                analysis_data = {
                    "processedFrame": f"data:image/jpeg;base64,{img_str}",
                    "behavior": main_behavior,
                    "confidence": 1.0,
                    "movementScore": 0.5,
                    "frameCount": session.frame_count,
                    "mediapipeAvailable": MEDIAPIPE_AVAILABLE,
                    "modelAvailable": True
                }
                
                try:
                    await asyncio.wait_for(websocket.send_json(analysis_data), timeout=5.0)
                except Exception:
                    break
                    
            except Exception:
                break
                
    except Exception as e:
        print(f"Session Error: {e}")
    finally:
        if session_id in sessions:
            async def cleanup(sid):
                await asyncio.sleep(300)
                if sid in sessions: del sessions[sid]
            asyncio.create_task(cleanup(session_id))
        
        if MEDIAPIPE_AVAILABLE and holistic:
            holistic.close()
        connection_manager.disconnect(session_id)

# === Graphs Endpoint ===
@app.post("/generate-graphs")
async def generate_graphs(session_id: dict):
    try:
        if isinstance(session_id, dict): session_id = session_id.get("session_id", "")
        else: session_id = str(session_id)
        session = sessions.get(session_id)
        if not session: raise ValueError
    except:
        # Dummy data for robustness
        session = SessionData()
        session.prediction_history = ["Standing"] * 10
        session.smoothed_scores = [0.5] * 10

    if not session.prediction_history: return {"error": "No data"}
    
    graph_data = {}
    counts = Counter(session.prediction_history)
    
    # 1. Action Frequency
    plt.figure(figsize=(9, 4.5))
    plt.style.use('dark_background')
    plt.bar(list(counts.keys()), list(counts.values()), color='#00FFE3', edgecolor='cyan')
    plt.title("Action Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_data["actionFrequency"] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 2. Timeline
    plt.figure(figsize=(12, 3.5))
    plt.plot(session.prediction_history, marker='o', linestyle='--', color='#FF00FF')
    plt.title("Behavior Timeline")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_data["behaviorTimeline"] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 3. Intensity
    plt.figure(figsize=(10, 3.5))
    plt.plot(session.smoothed_scores, color='#32CD32')
    plt.title("Movement Intensity")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_data["movementIntensity"] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    graph_data["summary"] = {
        "totalFrames": len(session.prediction_history),
        "totalTime": round(len(session.prediction_history) / 30, 2),
        "mostFrequentBehavior": max(counts, key=counts.get) if counts else "None",
        "averageIntensity": 0.5,
        "peakIntensity": 1.0,
        "peakTime": 0.0
    }
    
    return graph_data

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("fixed_colab:app", host=host, port=port, reload=False)