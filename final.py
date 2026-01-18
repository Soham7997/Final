from ultralytics import YOLO
import cv2
import sys

# Load trained model
model = YOLO("best.pt")

# Check command line arguments
if len(sys.argv) > 1:
    choice = sys.argv[1]
    if len(sys.argv) > 2:
        video_path = sys.argv[2]
    else:
        video_path = "test_video3.mp4"
else:
    # Fallback to user input
    print("Select input source:")
    print("1 - Video file")
    print("2 - Webcam")

    choice = input("Enter your choice (1 or 2): ").strip()

if choice == "1":
    if 'video_path' not in locals():
        video_path = "test_video3.mp4"   # change if needed
    cap = cv2.VideoCapture(video_path)
    print("[INFO] Running inference on VIDEO file")

elif choice == "2":
    cap = cv2.VideoCapture(1)        # Try camera index 1 if 0 fails
    print("[INFO] Running inference on WEBCAM")

else:
    print("[ERROR] Invalid choice. Please enter 1 or 2.")
    exit()

# ---------------- INFERENCE LOOP ----------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("[INFO] Stream ended or camera not available.")
        break

    # Run YOLO inference
    results = model.predict(
        source=frame,
        imgsz=640,
        conf=0.6,      # confidence threshold
        iou=0.5,       # IoU threshold (0 is NOT recommended)
        device='cpu',  # Use CPU since no GPU available
        verbose=False
    )

    # Print detections
    for result in results:
        if result.boxes:
            for box in result.boxes:
                cls = int(box.cls)
                conf = box.conf.item()
                class_name = model.names[cls]
                print(f"Detected: {class_name} with confidence {conf:.2f}")

    # Draw bounding boxes
    annotated_frame = results[0].plot()

    # Show live preview
    cv2.imshow("YOLOv8 Video Inference", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
