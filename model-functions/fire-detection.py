import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 model
model = YOLO(r"models\fire-detection-model.pt", task="segment")

# Open video capture

cap = cv2.VideoCapture(r"E:\coding\project\fire-smoke-detection\sample-media\f3.mp4")
# cap = cv2.VideoCapture(r"E:\coding\project\fire-smoke-detection\sample-media\f2.mp4")


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame)
    
    # Process each detection
    for result in results[0].boxes:
        # Get box coordinates
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        
        # Get confidence and class
        confidence = float(result.conf[0])
        class_id = int(result.cls[0])
        class_name = model.names[class_id]
        
        if confidence > 0.2:  # Confidence threshold
            # Draw box
            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
            
            cvzone.cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), l=5,t=3, rt=1, colorC=(0, 0, 255), colorR=(0, 165, 255))
            
            # Add label
            label = f'{class_name.upper()} {confidence*100:.1f}%'
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cvzone.putTextRect(frame, label, (x1, y1 - 10), 0.8, 1, (255, 255, 255), (0, 0, 255), colorB=(0, 255, 0))
    
    # Display the frame
    cv2.imshow("YOLOv11 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()