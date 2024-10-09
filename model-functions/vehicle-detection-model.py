import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 model
model = YOLO(r"E:\coding\project\vehicle-detection-model\runs\kaggle\working\runs\detect\train\weights\best.pt", task="detect")

# Open video capture
cap = cv2.VideoCapture(r"E:\coding\project\vehicle-detection-model\media-sample\v1.mp4")
# Define colors for different vehicle classes (BGR format)
class_colors = {
    # Cars (Green family)
    'car': (0, 255, 0),        # Pure Green
    
    # Buses (Blue family)
    'big bus': (255, 50, 0),   # Dark Blue
    'bus-l-': (255, 150, 0),   # Medium Blue
    'bus-s-': (255, 200, 0),   # Light Blue
    'small bus': (255, 250, 0), # Very Light Blue
    
    # Trucks (Red family)
    'truck-xl-': (0, 0, 255),  # Pure Red
    'big truck': (0, 0, 220),  # Slightly Darker Red
    'truck-l-': (0, 0, 190),   # Dark Red
    'mid truck': (0, 50, 180), # Dark Red with slight blue
    'truck-m-': (0, 70, 170),  # Medium Red
    'small truck': (20, 90, 160), # Light Red
    'truck-s-': (40, 110, 150), # Very Light Red
}

# Default color for undefined classes
DEFAULT_COLOR = (128, 128, 128)  # Gray



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
        
        if confidence > 0.4:  # Confidence threshold
            # Get color for the detected class
            color = class_colors.get(class_name.lower(), DEFAULT_COLOR)
            
            # Draw box with class-specific color
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Add label with matching color
            label = f'{class_name} {confidence*100:.2f}%'
            
            # Calculate optimal text position
            text_y = max(y1 - 10, 20)  # Ensure text doesn't go above frame
            
            # Create background for text that matches vehicle class color
            cvzone.putTextRect(frame, 
                             label, 
                             (x1, text_y), 
                             scale=0.8,  # Slightly smaller text for better fit
                             thickness=1,
                             colorR=color,          # Rectangle color
                             colorT=(255, 255, 255),  # Text color (white)
                             offset=5,              # Padding around text
                             border=2)              # Border thickness
    
    # Add legend to the frame
    legend_y = 30
    for class_name, color in class_colors.items():
        cv2.putText(frame, 
                   class_name, 
                   (10, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, 
                   color, 
                   2)
        legend_y += 20
    
    # Display the frame with class name
    cv2.imshow("Vehicle Detection with Colors", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

