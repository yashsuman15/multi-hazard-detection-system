import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
from pathlib import Path
from tkinter import filedialog
from ultralytics import YOLO
from prototype1 import UnifiedDetectionSystem

class HazardDetectionGUI:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Multi Hazard Detection System")
        self.root.geometry("1280x720")
        
        # Initialize detection system
        self.detector = UnifiedDetectionSystem()
        
        # Video handling variables
        self.video_source = None
        self.cap = None
        self.is_running = False
        self.current_mode = None
        
        self.create_gui()
        
    def create_gui(self):
        # Create main frame layout
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left panel for controls
        self.control_panel = ctk.CTkFrame(self.main_frame, width=200)
        self.control_panel.pack(side="left", fill="y", padx=5, pady=5)
        
        # Create video display area
        self.video_frame = ctk.CTkFrame(self.main_frame)
        self.video_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="No video loaded")
        self.video_label.pack(fill="both", expand=True)
        
        # Add controls
        self.create_control_panel()
        
    def create_control_panel(self):
        # Title
        title_label = ctk.CTkLabel(
            self.control_panel, 
            text="Detection Controls",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Video source selection
        source_frame = ctk.CTkFrame(self.control_panel)
        source_frame.pack(fill="x", padx=5, pady=5)
        
        self.source_button = ctk.CTkButton(
            source_frame,
            text="Select Video",
            command=self.select_video_source
        )
        self.source_button.pack(fill="x", pady=5)
        
        self.source_label = ctk.CTkLabel(source_frame, text="No file selected")
        self.source_label.pack(pady=5)
        
        # Detection mode buttons
        modes_label = ctk.CTkLabel(
            self.control_panel,
            text="Detection Modes",
            font=("Helvetica", 14, "bold")
        )
        modes_label.pack(pady=10)
        
        modes = [
            ("Crowd Detection", "crowd"),
            ("Fire Detection", "fire"),
            ("Smoking Detection", "smoking"),
            ("Vehicle Detection", "vehicle"),
            ("Weapon Detection", "weapon")
        ]
        
        for mode_text, mode_value in modes:
            btn = ctk.CTkButton(
                self.control_panel,
                text=mode_text,
                command=lambda m=mode_value: self.set_detection_mode(m)
            )
            btn.pack(pady=5, padx=10, fill="x")
        
        # Start/Stop button
        self.start_stop_btn = ctk.CTkButton(
            self.control_panel,
            text="Start Detection",
            command=self.toggle_detection,
            fg_color="green"
        )
        self.start_stop_btn.pack(pady=20, padx=10, fill="x")
        
    def select_video_source(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            self.video_source = file_path
            self.source_label.configure(text=Path(file_path).name)
            
    def set_detection_mode(self, mode):
        self.current_mode = mode
        
    def toggle_detection(self):
        if not self.video_source:
            return
            
        if not self.is_running:
            self.start_detection()
        else:
            self.stop_detection()
            
    def start_detection(self):
        self.is_running = True
        self.start_stop_btn.configure(text="Stop Detection", fg_color="red")
        
        # Start video processing in a separate thread
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()
        
    def stop_detection(self):
        self.is_running = False
        self.start_stop_btn.configure(text="Start Detection", fg_color="green")
        if self.cap:
            self.cap.release()
            
    def process_video(self):
        self.cap = cv2.VideoCapture(self.video_source)
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Apply detection based on current mode
            detection_frame = frame.copy()
            if self.current_mode == 'crowd':
                frame = self.detector.crowd_detection(detection_frame)
            elif self.current_mode == 'fire':
                frame = self.detector.fire_detection(detection_frame)
            elif self.current_mode == 'smoking':
                frame = self.detector.smoking_detection(detection_frame)
            elif self.current_mode == 'vehicle':
                frame = self.detector.vehicle_detection(detection_frame)
            elif self.current_mode == 'weapon':
                frame = self.detector.weapon_detection(detection_frame)
                
            # Add model indicator
            self.detector.add_model_indicator(frame, self.current_mode)
            
            # Convert to PhotoImage and update GUI
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            
            # Update label in main thread
            self.video_label.configure(image=img)
            self.video_label.image = img
            
        self.cap.release()
        
    def run(self):
        self.root.mainloop()

def main():
    app = HazardDetectionGUI()
    app.run()

if __name__ == "__main__":
    main()