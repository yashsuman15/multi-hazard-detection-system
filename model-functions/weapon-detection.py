import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 model
model = YOLO(r'E:\coding\project\weapon detection\runs\detect\train3\weights\best.pt', task="detect")

# Open video capture
cap = cv2.VideoCapture(r"E:\coding\project\weapon detection\w12.mp4")
# cap = cv2.VideoCapture(0)

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
        class_name = " GUN "
        
        if confidence > 0.2:  # Confidence threshold
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
            
            # Add label
            label = f'{class_name} {confidence *100:.2f}%'
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cvzone.putTextRect(frame, label, (x1, y1 - 10), 1, 1, (255, 255, 255), (0, 0, 255), colorB=(0, 255, 0))
    
    # Display the frame
    cv2.imshow("YOLOv11 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()