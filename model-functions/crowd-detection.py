import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 model
model = YOLO(r'models\crowd-density-model.pt', task="detect")

# Open video capture
cap = cv2.VideoCapture(r"E:\coding\project\crowd-density-model\sample-media\c3.webm")
# cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame)
    
    # Initialize counter for this frame
    person_count = 0
    
    # Process each detection
    for idx, result in enumerate(results[0].boxes):
        # Get box coordinates
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        
        # Get confidence and class
        confidence = float(result.conf[0])
        class_id = int(result.cls[0])
        
        if confidence > 0.3:  # Confidence threshold
            # Increment counter
            person_count += 1
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 1)
            
            # Add count label for each box
            box_label = f'{person_count}'
            # cvzone.putTextRect(frame, box_label, (x1, y1 - 10), scale=1, thickness=1,colorR=(255,0,255), colorB=(0,0,0))
            cv2.putText(frame, box_label, (x1+10, y1+20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    # Add total count in top left corner
    total_label = f'People Count: {person_count}'
    cvzone.putTextRect(frame, total_label, (20, 40),
                      scale=1, thickness=1,
                      colorR=(0,0,0), colorB=(0,0,0))
    
    # Display the frame
    cv2.imshow("Crowd-Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()