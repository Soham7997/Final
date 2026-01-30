import cv2
import mediapipe as mp
from deepface import DeepFace
import threading

# --- 1. CONFIGURATION ---
# DeepFace is heavy, so we run it in a separate thread to keep the video smooth.
detect_every_n_frames = 15  # Analyze face every 15 frames
frame_counter = 0
current_emotion = "Neutral"
is_shouting = False

# --- 2. SETUP MEDIAPIPE ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
# Initialize Holistic (tracks Face, Hands, and Pose)
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# --- 3. HELPER FUNCTION FOR EMOTION ---
def analyze_emotion(img):
    global current_emotion, is_shouting
    try:
        # Enforce detection=False prevents crashing if no face is found
        objs = DeepFace.analyze(img_path=img, actions=['emotion'], enforce_detection=False, silent=True)
        if objs:
            result = objs[0]
            current_emotion = result['dominant_emotion']
            
            # Simple logic: If angry and dominant probability is high -> Check mouth later
            # (Refined shouting logic happens in the main loop using geometry)
    except Exception as e:
        pass

# --- 4. MAIN LOOP ---
cap = cv2.VideoCapture(0) # <--- This fixes your NameError

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for mirror view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = holistic.process(rgb_frame)
    
    # --- LOGIC: HAND RAISING ---
    hand_status = ""
    if results.pose_landmarks:
        # MediaPipe Indices: 16=Right Wrist, 15=Left Wrist, 6=Right Eye, 3=Left Eye
        landmarks = results.pose_landmarks.landmark
        
        right_wrist_y = landmarks[16].y
        right_eye_y = landmarks[6].y
        left_wrist_y = landmarks[15].y
        left_eye_y = landmarks[3].y
        
        # Note: In computer vision, Y decreases as you go UP.
        if right_wrist_y < right_eye_y or left_wrist_y < left_eye_y:
            hand_status = "HAND RAISED"
            # Draw a green rectangle to visualize
            cv2.rectangle(frame, (10, 10), (630, 60), (0, 255, 0), -1)

    # --- LOGIC: EMOTION ANALYSIS (Threaded) ---
    if frame_counter % detect_every_n_frames == 0:
        # Run deepface in background so video doesn't freeze
        threading.Thread(target=analyze_emotion, args=(frame.copy(),)).start()
    
    # --- LOGIC: SHOUTING DETECTION (Geometry) ---
    # We combine "Angry" emotion with "Mouth Open" geometry
    mouth_status = ""
    if results.face_landmarks:
        # MediaPipe FaceMesh Indices: 13=Upper Lip, 14=Lower Lip
        face_lm = results.face_landmarks.landmark
        upper_lip_y = face_lm[13].y
        lower_lip_y = face_lm[14].y
        
        # Calculate distance
        mouth_open_dist = abs(upper_lip_y - lower_lip_y)
        
        # Threshold: 0.05 is a standard "open" value, tune this if needed
        if mouth_open_dist > 0.05:
            if current_emotion in ["angry", "fear", "surprise"]:
                mouth_status = "SHOUTING / SCREAMING"
            else:
                mouth_status = "Mouth Open"

    frame_counter += 1

    # --- DRAWING TEXT ---
    # 1. Hand Status
    if hand_status:
        cv2.putText(frame, hand_status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # 2. Emotion Status
    color = (0, 0, 255) if current_emotion in ["angry", "sad"] else (255, 0, 0)
    display_text = f"Emotion: {current_emotion}"
    if mouth_status == "SHOUTING / SCREAMING":
        display_text = "!!! SHOUTING !!!"
        color = (0, 0, 255) # Red
        
    cv2.putText(frame, display_text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('Expression & Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()