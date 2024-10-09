import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 model
model = YOLO(r'models\smoking-detection-model.pt', task="detect")

# Open video capture

cap = cv2.VideoCapture(r"E:\coding\project\Smoking-Detection\media\samples\v8.webm")


def iou(boxA, boxB):
    # Compute the intersection over union (IoU) between two bounding boxes
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    
    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)
    
    # Compute the area of both the prediction and ground-truth rectangles
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    
    # Compute the intersection over union by taking the intersection area
    # and dividing it by the sum of prediction + ground-truth areas - intersection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    
    return iou

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame)
    
    face_boxes = []  # To store face bounding boxes
    smoking_boxes = []  # To store smoking bounding boxes

    # First pass to gather face and smoking boxes
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        confidence = float(result.conf[0])
        class_id = int(result.cls[0])

        if confidence > 0.5:
            if class_id == 1:  # class 1: face
                face_boxes.append((x1, y1, x2, y2))
            elif class_id == 2:  # class 2: smoking
                smoking_boxes.append((x1, y1, x2, y2))

    # Second pass to draw boxes, ensuring class 2 takes precedence over class 1
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        confidence = float(result.conf[0])
        class_id = int(result.cls[0])
        class_name = model.names[class_id]

        if confidence > 0.2:
            # Always draw class 0 (cigarette)
            if class_id == 0:
                label = f'{class_name} {confidence *100:.2f}%'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 1)
                # cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                cvzone.putTextRect(frame, label, (x1, y1 - 10), 0.6, 1, (255, 255, 255), (0, 165, 255), colorB=(0, 255, 0))

            # Only draw class 1 (face) if there is no overlapping class 2 (smoking)
            elif class_id == 1:
                should_draw_face = True
                for smoking_box in smoking_boxes:
                    if iou((x1, y1, x2, y2), smoking_box) > 0.3:  # Threshold for overlap
                        should_draw_face = False
                        break
                
                if should_draw_face:
                    label = f'{class_name} {confidence*100:.2f}%'
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 1)
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # Always draw class 2 (smoking)
            elif class_id == 2:
                label = f'{class_name} {confidence *100:.2f}%'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cvzone.putTextRect(frame, label, (x1, y1 - 10), 1, 1, (255, 255, 255), (0, 0, 255), colorB=(0, 255, 0))

    # Display the frame
    cv2.imshow("SMOKING DETECTION", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
