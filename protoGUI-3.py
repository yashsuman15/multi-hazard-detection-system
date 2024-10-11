import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
from pathlib import Path
from tkinter import filedialog
from ultralytics import YOLO
from prototype1 import UnifiedDetectionSystem
from datetime import datetime
import os

class HazardDetectionGUI:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Multi Hazard Detection System")
        self.root.geometry("1280x720")
        
        # Set color theme
        ctk.set_appearance_mode("dark")
        self.root.configure(fg_color="black")
        
        # Initialize detection system
        self.detector = UnifiedDetectionSystem()
        
        # Video handling variables
        self.video_source = None
        self.cap = None
        self.is_running = False
        self.current_mode = None
        self.detection_active = False
        self.video_playing = False
        self.current_frame_pos = 0
        
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.create_gui()
        
    def create_gui(self):
        # Create main frame layout with dark theme
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#101010")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left panel for controls
        self.control_panel = ctk.CTkFrame(self.main_frame, width=200, fg_color="#151515")
        self.control_panel.pack(side="right", fill="y", padx=5, pady=5)
        
        # Create video display area
        self.video_frame = ctk.CTkFrame(self.main_frame, fg_color="#080808")
        self.video_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="No video loaded", text_color="#CCCCCC")
        self.video_label.pack(fill="both", expand=True)
        
        # Add controls
        self.create_control_panel()
        
        # Add creator credit at the bottom
        credit_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        credit_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        
        credit_label = ctk.CTkLabel(
            credit_frame,
            text="Created by: Yash Raj Suman",
            font=("Helvetica", 12),
            text_color="#808080"
        )
        credit_label.pack(side="right", padx=10)
        
    def create_control_panel(self):
        # Title
        title_label = ctk.CTkLabel(
            self.control_panel, 
            text="Detection Controls",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=10)
        
        # Video source selection
        source_frame = ctk.CTkFrame(self.control_panel, fg_color="#202020")
        source_frame.pack(fill="x", padx=5, pady=5)
        
        self.source_button = ctk.CTkButton(
            source_frame,
            text="Select Video",
            command=self.select_video_source,
            fg_color="#303030",
            hover_color="#404040"
        )
        self.source_button.pack(fill="x", pady=5)
        
        self.source_label = ctk.CTkLabel(source_frame, text="No file selected", text_color="#AAAAAA")
        self.source_label.pack(pady=5)
        
        # Video control buttons
        video_controls = ctk.CTkFrame(self.control_panel, fg_color="#202020")
        video_controls.pack(fill="x", padx=5, pady=5)
        
        self.play_pause_btn = ctk.CTkButton(
            video_controls,
            text="Play Video",
            command=self.toggle_video,
            fg_color="#252525",
            hover_color="#353535"
        )
        self.play_pause_btn.pack(pady=5, padx=10, fill="x")
        
        self.restart_btn = ctk.CTkButton(
            video_controls,
            text="Restart Video",
            command=self.restart_video,
            fg_color="#252525",
            hover_color="#353535"
        )
        self.restart_btn.pack(pady=5, padx=10, fill="x")
        
        self.screenshot_btn = ctk.CTkButton(
            video_controls,
            text="Take Screenshot",
            command=self.take_screenshot,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A"
        )
        self.screenshot_btn.pack(pady=5, padx=10, fill="x")
        
        # Detection mode buttons
        modes_label = ctk.CTkLabel(
            self.control_panel,
            text="Detection Modes",
            font=("Helvetica", 14, "bold"),
            text_color="#FFFFFF"
        )
        modes_label.pack(pady=10)
        
        modes = [
            ("👥 Crowd Detection", "crowd"),
            ("🔥 Fire Detection", "fire"),
            ("🚬 Smoking Detection", "smoking"),
            ("🚗 Vehicle Detection", "vehicle"),
            ("⚠️ Weapon Detection", "weapon")
        ]
        
        for mode_text, mode_value in modes:
            btn = ctk.CTkButton(
                self.control_panel,
                text=mode_text,
                command=lambda m=mode_value: self.set_detection_mode(m),
                # fg_color="#202020",
                # hover_color="#303030"
            )
            btn.pack(pady=5, padx=10, fill="x")
        
        # Detection control button
        self.detection_btn = ctk.CTkButton(
            self.control_panel,
            text="Start Detection",
            command=self.toggle_detection,
            fg_color="green",
            # hover_color="#2A2A2A"
        )
        self.detection_btn.pack(pady=20, padx=10, fill="x")

    # Rest of the methods remain the same as they don't affect the appearance
    def select_video_source(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            self.video_source = file_path
            self.source_label.configure(text=Path(file_path).name)
            self.current_frame_pos = 0
            
    def set_detection_mode(self, mode):
        self.current_mode = mode
        
    def toggle_detection(self):
        if not self.video_playing:
            return
            
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.detection_btn.configure(text="Stop Detection", fg_color="#2A1A1A")
        else:
            self.detection_btn.configure(text="Start Detection", fg_color="#1A1A1A")
            
    def toggle_video(self):
        if not self.video_source:
            return
            
        if not self.video_playing:
            self.start_video()
        else:
            self.pause_video()
            
    def start_video(self):
        self.video_playing = True
        self.play_pause_btn.configure(text="Pause Video", fg_color="#2A2A2A")
        
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.video_source)
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_pos)
        
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()
        
    def pause_video(self):
        self.video_playing = False
        self.play_pause_btn.configure(text="Resume Video", fg_color="#252525")
        
    def restart_video(self):
        self.current_frame_pos = 0
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.video_playing:
            self.start_video()
        else:
            self.cap = cv2.VideoCapture(self.video_source)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
    def take_screenshot(self):
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            print(f"Screenshot saved as {filename}")
            
    def process_video(self):
        while self.video_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.video_playing = False
                self.play_pause_btn.configure(text="Play Video", fg_color="#252525")
                self.current_frame_pos = 0
                break
                
            self.current_frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            self.current_frame = frame.copy()
            
            if self.detection_active and self.current_mode:
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
                    
                self.detector.add_model_indicator(frame, self.current_mode)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            
            self.video_label.configure(image=img, text="")
            self.video_label.image = img
        
    def run(self):
        self.root.mainloop()

def main():
    app = HazardDetectionGUI()
    app.run()

if __name__ == "__main__":
    main()