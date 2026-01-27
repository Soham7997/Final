import cv2
import mediapipe as mp
import math

class HumanRealtimeAnalyzer:
    def __init__(self):
        # ---- Pose ----
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # ---- Face ----
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_draw = mp.solutions.drawing_utils

    # ---------------- UTILS ----------------
    def _distance(self, a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    # ---------------- ANALYZE ----------------
    def analyze(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_results = self.pose.process(rgb)
        face_results = self.face_mesh.process(rgb)

        output = {
            "left_hand_raised": False,
            "right_hand_raised": False,
            "expression": "Neutral",
            "pose_landmarks": None,
            "face_landmarks": None
        }

        # -------- POSE --------
        if pose_results.pose_landmarks:
            lm = pose_results.pose_landmarks.landmark

            lw = lm[self.mp_pose.PoseLandmark.LEFT_WRIST]
            ls = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]

            rw = lm[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            rs = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            output["left_hand_raised"] = lw.y < ls.y
            output["right_hand_raised"] = rw.y < rs.y
            output["pose_landmarks"] = pose_results.pose_landmarks

        # -------- FACE & EXPRESSIONS --------
        if face_results.multi_face_landmarks:
            lm = face_results.multi_face_landmarks[0].landmark
            output["face_landmarks"] = face_results.multi_face_landmarks[0]

            # ---- Key landmarks ----
            mouth_left = lm[61]
            mouth_right = lm[291]
            upper_lip = lm[13]
            lower_lip = lm[14]

            left_eye_top = lm[159]
            left_eye_bottom = lm[145]

            brow_left = lm[70]
            brow_right = lm[300]

            # ---- Metrics ----
            mouth_width = self._distance(mouth_left, mouth_right)
            mouth_open = self._distance(upper_lip, lower_lip)
            eye_open = self._distance(left_eye_top, left_eye_bottom)
            brow_distance = self._distance(brow_left, brow_right)

            # ---- Expression rules ----
            if mouth_open > 0.045:
                expression = "Shouting / Surprised"

            elif mouth_width > 0.08 and mouth_open > 0.02:
                expression = "Happy"

            elif mouth_open < 0.015 and brow_distance < 0.18:
                expression = "Angry"

            elif mouth_open < 0.015 and eye_open < 0.015:
                expression = "Sad"

            elif mouth_open < 0.012 and mouth_width < 0.06:
                expression = "Melancholy"

            else:
                expression = "Neutral"

            output["expression"] = expression

        return output

    # ---------------- DRAW ----------------
    def draw(self, frame, data):
        y = 35

        if data["left_hand_raised"]:
            cv2.putText(frame, "LEFT HAND RAISED", (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,255,0), 2)
            y += 30

        if data["right_hand_raised"]:
            cv2.putText(frame, "RIGHT HAND RAISED", (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,255,0), 2)
            y += 30

        cv2.putText(frame, f"Expression: {data['expression']}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,0), 2)

        if data["pose_landmarks"]:
            self.mp_draw.draw_landmarks(
                frame,
                data["pose_landmarks"],
                self.mp_pose.POSE_CONNECTIONS
            )

        if data["face_landmarks"]:
            self.mp_draw.draw_landmarks(
                frame,
                data["face_landmarks"],
                self.mp_face.FACEMESH_TESSELATION
            )


# ---------------- MAIN ----------------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    analyzer = HumanRealtimeAnalyzer()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data = analyzer.analyze(frame)
        analyzer.draw(frame, data)

        cv2.imshow("Human Real-Time Analysis", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
