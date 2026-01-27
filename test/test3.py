import cv2
import mediapipe as mp
from deepface import DeepFace
import threading
import numpy as np
import time

# --- 1. CONFIGURATION ---
detect_every_n_frames = 10  # DeepFace frequency
frame_counter = 0

# We use this list to share data between the Thread and the Main Loop
# Structure: [{'box': (x,y,w,h), 'emotion': 'happy', 'center': (cx, cy)}]
cached_emotions = [] 

# --- 2. SETUP ---
# A. MediaPipe (For Body/Pose of main person)
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# B. Haar Cascade (For fast Multi-Face detection)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- 3. HELPER FUNCTIONS ---

def calculate_angle(a, b, c):
    """Calculates angle between three points (a-b-c)"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360-angle
    return angle

def analyze_emotions_multithread(frame_copy):
    """
    Runs DeepFace on the full image to find ALL faces and their emotions.
    """
    global cached_emotions
    try:
        # 'opencv' backend is faster for real-time video
        results = DeepFace.analyze(
            img_path=frame_copy, 
            actions=['emotion'], 
            enforce_detection=False, 
            silent=True,
            detector_backend='opencv' 
        )
        
        # Ensure results is a list (DeepFace versions vary)
        if isinstance(results, dict):
            results = [results]
            
        new_data = []
        for res in results:
            # DeepFace returns the face region
            region = res['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            
            # Calculate center to match with real-time boxes later
            center = (x + w//2, y + h//2)
            
            new_data.append({
                'box': (x, y, w, h),
                'emotion': res['dominant_emotion'],
                'center': center
            })
            
        cached_emotions = new_data
        
    except Exception as e:
        pass # Ignore glitches in detection

# --- 4. MAIN LOOP ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # Flip frame for mirror view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # ==================================================
    # PART A: BODY & POSE TRACKING (Main Person)
    # MediaPipe Holistic is single-person only.
    # ==================================================
    results = holistic.process(rgb_frame)
    
    active_statuses = [] 
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # 1. Hands Up Logic
        right_wrist = landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST]
        right_eye = landmarks[mp_holistic.PoseLandmark.RIGHT_EYE]
        left_wrist = landmarks[mp_holistic.PoseLandmark.LEFT_WRIST]
        left_eye = landmarks[mp_holistic.PoseLandmark.LEFT_EYE]
        
        if right_wrist.y < right_eye.y: active_statuses.append("RIGHT HAND UP")
        if left_wrist.y < left_eye.y: active_statuses.append("LEFT HAND UP")

        # 2. Standing/Sitting Logic
        l_hip = [landmarks[23].x, landmarks[23].y]
        l_knee = [landmarks[25].x, landmarks[25].y]
        l_ankle = [landmarks[27].x, landmarks[27].y]
        
        if landmarks[25].visibility > 0.5 and landmarks[27].visibility > 0.5:
            knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            if knee_angle > 160: active_statuses.append("STANDING")
            elif knee_angle < 140: active_statuses.append("SITTING")

        # Draw Skeleton
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

    # ==================================================
    # PART B: MULTI-FACE EMOTION & BOUNDING BOXES
    # ==================================================
    
    # 1. Run DeepFace in background thread (Slow, accurate)
    if frame_counter % detect_every_n_frames == 0:
        threading.Thread(target=analyze_emotions_multithread, args=(frame.copy(),)).start()
    
    # 2. Run Haar Cascade (Fast, every frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # 3. Match Fast Boxes to Slow Emotions
    for (x, y, w, h) in faces:
        curr_cx = x + w // 2
        curr_cy = y + h // 2
        
        # Default if analysis isn't ready
        current_display_emotion = "Detecting..." 
        
        # Find closest match in cached_emotions
        min_dist = 10000
        for cached in cached_emotions:
            c_cx, c_cy = cached['center']
            dist = np.sqrt((curr_cx - c_cx)**2 + (curr_cy - c_cy)**2)
            
            # If faces are close enough (within 100px), assume it's the same person
            if dist < 100 and dist < min_dist:
                min_dist = dist
                current_display_emotion = cached['emotion']

        # Determine Color (Red for Angry/Fear, Green for others)
        color = (0, 255, 0)
        if current_display_emotion in ['angry', 'fear', 'sad']:
            color = (0, 0, 255)
            
        # Draw Bounding Box
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Draw Label Background (for readability)
        cv2.rectangle(frame, (x, y-30), (x+w, y), color, -1)
        cv2.putText(frame, current_display_emotion, (x + 5, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # --- DISPLAY STATUSES ---
    y_pos = 30
    for status in active_statuses:
        color = (255, 255, 0) if status == "STANDING" else (0, 255, 0)
        cv2.putText(frame, f"Main Body: {status}", (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y_pos += 30

    frame_counter += 1
    cv2.imshow('Multi-Face & Body Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()