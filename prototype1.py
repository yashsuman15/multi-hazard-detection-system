import cv2
from ultralytics import YOLO
import cvzone

class UnifiedDetectionSystem:
    def __init__(self):
        # Initialize all models
        self.crowd_model = YOLO('models/crowd-density-model.pt', task="detect")
        self.fire_model = YOLO('models/fire-detection-model.pt', task="segment")
        self.smoking_model = YOLO('models/smoking-detection-model.pt', task="detect")
        self.vehicle_model = YOLO('models/vehicle-detection-model.pt', task="detect")
        self.weapon_model = YOLO('models/weapon-detection-model.pt', task="detect")
        
        # Model descriptions for display
        self.model_info = {
            'crowd': {'name': 'Crowd Detection', 'color': (0, 255, 0)},  # Green
            'fire': {'name': 'Fire Detection', 'color': (0, 69, 255)},   # Orange
            'smoking': {'name': 'Smoking Detection', 'color': (255, 0, 0)},  # Blue
            'vehicle': {'name': 'Vehicle Detection', 'color': (255, 255, 0)},  # Cyan
            'weapon': {'name': 'Weapon Detection', 'color': (0, 0, 255)}   # Red
        }
        
        # Vehicle detection colors
        self.vehicle_colors = {
            'car': (0, 255, 0),
            'big bus': (255, 50, 0),
            'bus-l-': (255, 150, 0),
            'bus-s-': (255, 200, 0),
            'small bus': (255, 250, 0),
            'truck-xl-': (0, 0, 255),
            'big truck': (0, 0, 220),
            'truck-l-': (0, 0, 190),
            'mid truck': (0, 50, 180),
            'truck-m-': (0, 70, 170),
            'small truck': (20, 90, 160),
            'truck-s-': (40, 110, 150),
        }
        self.DEFAULT_COLOR = (128, 128, 128)

    def add_model_indicator(self, frame, current_mode):
        if current_mode:
            # Get frame dimensions
            height, width = frame.shape[:2]
            
            # Get model info
            model_info = self.model_info[current_mode]
            indicator_text = f"ACTIVATED: {model_info['name']}"
            
            # Create background rectangle
            text_size = cv2.getTextSize(indicator_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            rect_width = text_size[0] + 20
            rect_height = text_size[1] + 20
            
            # Calculate position (lower right corner)
            rect_x = width - rect_width - 10
            rect_y = height - rect_height - 10
            
            # Draw semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, 
                         (rect_x, rect_y),
                         (width - 10, height - 10),
                         model_info['color'], 
                         -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw border
            cv2.rectangle(frame, 
                         (rect_x, rect_y),
                         (width - 10, height - 10),
                         model_info['color'], 
                         2)
            
            # Add text
            text_x = rect_x + 10
            text_y = height - 20
            cv2.putText(frame, 
                       indicator_text,
                       (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.7,
                       (255, 255, 255),
                       2)

    def crowd_detection(self, frame):
        results = self.crowd_model(frame)
        person_count = 0
        
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            
            if confidence > 0.3:
                person_count += 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 1)
                cv2.putText(frame, f'{person_count}', (x1+10, y1+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        total_label = f'People Count: {person_count}'
        cvzone.putTextRect(frame, total_label, (20, 40),
                          scale=1, thickness=1,
                          colorR=(0,0,0), colorB=(0,0,0))
        return frame

    def fire_detection(self, frame):
        results = self.fire_model(frame)
        
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_id = int(result.cls[0])
            class_name = self.fire_model.names[class_id]
            
            if confidence > 0.2:
                cvzone.cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), 
                                l=5, t=3, rt=1, colorC=(0, 0, 255), 
                                colorR=(0, 165, 255))
                
                label = f'{class_name.upper()} {confidence*100:.1f}%'
                cvzone.putTextRect(frame, label, (x1, y1 - 10), 0.8, 1, 
                                 (255, 255, 255), (0, 0, 255), 
                                 colorB=(0, 255, 0))
        return frame

    def smoking_detection(self, frame):
        results = self.smoking_model(frame)
        
        face_boxes = []
        smoking_boxes = []

        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_id = int(result.cls[0])

            if confidence > 0.5:
                if class_id == 1:
                    face_boxes.append((x1, y1, x2, y2))
                elif class_id == 2:
                    smoking_boxes.append((x1, y1, x2, y2))

        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_id = int(result.cls[0])
            class_name = self.smoking_model.names[class_id]

            if confidence > 0.2:
                if class_id == 0:
                    label = f'{class_name} {confidence*100:.2f}%'
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 1)
                    cvzone.putTextRect(frame, label, (x1, y1 - 10), 0.6, 1, 
                                     (255, 255, 255), (0, 165, 255), 
                                     colorB=(0, 255, 0))
                
                elif class_id == 2:
                    label = f'{class_name} {confidence*100:.2f}%'
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cvzone.putTextRect(frame, label, (x1, y1 - 10), 1, 1, 
                                     (255, 255, 255), (0, 0, 255), 
                                     colorB=(0, 255, 0))
        return frame

    def vehicle_detection(self, frame):
        results = self.vehicle_model(frame)
        
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_id = int(result.cls[0])
            class_name = self.vehicle_model.names[class_id]
            
            if confidence > 0.6:
                color = self.vehicle_colors.get(class_name.lower(), self.DEFAULT_COLOR)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                label = f'{class_name} {confidence*100:.2f}%'
                text_y = max(y1 - 10, 20)
                
                cvzone.putTextRect(frame, label, (x1, text_y), 
                                 scale=0.8, thickness=1,
                                 colorR=color, colorT=(255, 255, 255),
                                 offset=5, border=2)
        return frame

    def weapon_detection(self, frame):
        results = self.weapon_model(frame)
        
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_name = " GUN "
            
            if confidence > 0.2:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                
                label = f'{class_name} {confidence*100:.2f}%'
                cvzone.putTextRect(frame, label, (x1, y1 - 10), 1, 1, 
                                 (255, 255, 255), (0, 0, 255), 
                                 colorB=(0, 255, 0))
        return frame

def main():
    # Initialize the detection system
    detector = UnifiedDetectionSystem()
     
    video_path = r"sample-media\MHDS sample video 2.mp4"
    
    # Open video capture
    cap = cv2.VideoCapture(video_path)  # Use 0 for webcam or provide video path
    
    current_mode = None
    
    # Display instructions at startup
    print("\nUnified Detection System")
    print("------------------------")
    print("Press keys to switch detection modes:")
    print("1: Crowd Detection")
    print("2: Fire Detection")
    print("3: Smoking Detection")
    print("4: Vehicle Detection")
    print("5: Weapon Detection")
    print("Q: Quit")
    print("------------------------\n")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Create a copy of the frame for detection
        detection_frame = frame.copy()
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('1'):
            current_mode = 'crowd'
        elif key == ord('2'):
            current_mode = 'fire'
        elif key == ord('3'):
            current_mode = 'smoking'
        elif key == ord('4'):
            current_mode = 'vehicle'
        elif key == ord('5'):
            current_mode = 'weapon'
        elif key == ord('q'):
            break
        
        # Apply detection based on current mode
        if current_mode == 'crowd':
            frame = detector.crowd_detection(detection_frame)
        elif current_mode == 'fire':
            frame = detector.fire_detection(detection_frame)
        elif current_mode == 'smoking':
            frame = detector.smoking_detection(detection_frame)
        elif current_mode == 'vehicle':
            frame = detector.vehicle_detection(detection_frame)
        elif current_mode == 'weapon':
            frame = detector.weapon_detection(detection_frame)
        
        # Add model indicator to frame
        detector.add_model_indicator(frame, current_mode)
            
        # Display the frame
        cv2.imshow('Multi Hazard Detection System', frame)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()