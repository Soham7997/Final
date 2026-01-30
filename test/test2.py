import cv2
import mediapipe as mp
from deepface import DeepFace
import threading
import numpy as np
import math

# --- 1. CONFIGURATION ---
detect_every_n_frames = 15
frame_counter = 0
current_emotion = "Neutral"
is_shouting = False

# NEW: Global list to store data for multiple faces
# Format: [{'box': (x,y,w,h), 'emotion': 'happy'}, ...]
faces_data = []

# --- 2. SETUP MEDIAPIPE ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# --- 3. HELPER FUNCTIONS ---

def calculate_angle(a, b, c):
    """
    Calculates the angle at point b given three points [x, y]
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def analyze_emotion(img):
    global current_emotion, faces_data
    try:
        # Analyzes all faces in the image
        objs = DeepFace.analyze(img_path=img, actions=['emotion'], enforce_detection=False, silent=True)
        
        # If result is a dict (single face in older versions), wrap in list
        if isinstance(objs, dict):
            objs = [objs]
            
        temp_data = []
        if objs:
            # Update the main single emotion variable (for backward compatibility)
            current_emotion = objs[0]['dominant_emotion']
            
            # Extract box and emotion for EVERY face detected
            for obj in objs:
                region = obj['region']
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                emotion = obj['dominant_emotion']
                temp_data.append({'box': (x, y, w, h), 'emotion': emotion})
        
        # Update the global list safely
        faces_data = temp_data
        
    except Exception as e:
        print("Error in analysis:", e)
        pass

# --- 4. MAIN LOOP ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for mirror view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = holistic.process(rgb_frame)
    
    # Initialize status strings
    active_statuses = [] # Stores "Right Hand", "Standing", etc.
    mouth_status = ""

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # --- LOGIC A: LEFT VS RIGHT HAND ---
        # Get coordinates
        right_wrist = landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST]
        right_eye = landmarks[mp_holistic.PoseLandmark.RIGHT_EYE]
        left_wrist = landmarks[mp_holistic.PoseLandmark.LEFT_WRIST]
        left_eye = landmarks[mp_holistic.PoseLandmark.LEFT_EYE]
        
        # Check Right Hand (Person's anatomical right)
        if right_wrist.y < right_eye.y:
            active_statuses.append("RIGHT HAND UP")
            
        # Check Left Hand (Person's anatomical left)
        if left_wrist.y < left_eye.y:
            active_statuses.append("LEFT HAND UP")

        # --- LOGIC B: STANDING DETECTION ---
        # We need Hip, Knee, Ankle coordinates to calculate the leg angle
        # Using Left Leg for detection (Landmarks 23, 25, 27)
        l_hip = [landmarks[23].x, landmarks[23].y]
        l_knee = [landmarks[25].x, landmarks[25].y]
        l_ankle = [landmarks[27].x, landmarks[27].y]
        
        # Check visibility: If the camera can't see the knees, don't guess
        if landmarks[25].visibility > 0.5 and landmarks[27].visibility > 0.5:
            knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            
            # Angle > 160 degrees implies the leg is straight (Standing)
            if knee_angle > 160:
                active_statuses.append("STANDING")
            elif knee_angle < 140:
                active_statuses.append("SITTING")
        else:
            # Fallback if legs are hidden: Check if hips are visible but ankles are not
            # This part is optional/experimental based on camera framing
            pass

    # --- LOGIC C: EMOTION & SHOUTING ---
    if frame_counter % detect_every_n_frames == 0:
        # Pass a copy to the thread
        threading.Thread(target=analyze_emotion, args=(frame.copy(),)).start()
    
    if results.face_landmarks:
        face_lm = results.face_landmarks.landmark
        upper_lip_y = face_lm[13].y
        lower_lip_y = face_lm[14].y
        mouth_open_dist = abs(upper_lip_y - lower_lip_y)
        
        if mouth_open_dist > 0.05:
            if current_emotion in ["angry", "fear", "surprise"]:
                mouth_status = "SHOUTING"
            else:
                mouth_status = "Mouth Open"

    frame_counter += 1

    # --- VISUALIZATION ---
    # 1. Draw Active Body Statuses (Hands, Standing)
    y_pos = 50
    for status in active_statuses:
        color = (0, 255, 0) # Green
        if status == "STANDING": color = (255, 255, 0) # Cyan for standing
        cv2.putText(frame, status, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        y_pos += 40
    
    # 2. Draw Emotion & Bounding Boxes (UPDATED FOR MULTIPLE FACES)
    # Loop through all faces detected by DeepFace
    for face in faces_data:
        (x, y, w, h) = face['box']
        emotion_label = face['emotion']
        
        # Determine color based on emotion
        color_emo = (0, 255, 0) # Green default
        if emotion_label in ["angry", "sad", "fear"]:
            color_emo = (0, 0, 255) # Red for negative
            
        # Draw the box
        cv2.rectangle(frame, (x, y), (x+w, y+h), color_emo, 2)
        
        # Draw the emotion text above the box
        cv2.putText(frame, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_emo, 2)

    # Keep original text logic if shouting (Optional: overlay "SHOUTING" on box if preferred)
    if mouth_status == "SHOUTING":
        cv2.putText(frame, "!!! SHOUTING !!!", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Expression, Hands & Posture', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()