import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
from pathlib import Path
from tkinter import filedialog
from prototype1 import UnifiedDetectionSystem
from datetime import datetime
import os
import time
import psutil

try:
    import GPUtil
except ImportError:
    print("GPUtil not installed. GPU monitoring will be disabled.")
try:
    import wmi
except ImportError:
    print("wmi not installed. Temperature monitoring will be disabled.")

class SystemMonitor:
    def __init__(self):
        self.gpu_available = 'GPUtil' in globals()
        self.temp_available = 'wmi' in globals()
        if self.temp_available:
            self.wmi = wmi.WMI()
    
    def get_ram_usage(self):
        ram = psutil.virtual_memory()
        return f"RAM: {ram.percent}%"
    
    def get_gpu_usage(self):
        if not self.gpu_available:
            return "GPU: N/A"
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return f"GPU: {gpus[0].load * 100:.1f}%"
            return "GPU: Not found"
        except Exception:
            return "GPU: Error"
    
    def get_cpu_temp(self):
        if not self.temp_available:
            return "Temp: N/A"
        try:
            temperatures = []
            for temperature in self.wmi.MSAcpi_ThermalZoneTemperature():
                # Convert temperature from decikelvin to celsius
                temp_celsius = (temperature.CurrentTemperature / 10.0) - 273.15
                temperatures.append(temp_celsius)
            if temperatures:
                avg_temp = sum(temperatures) / len(temperatures)
                return f"CPU: {avg_temp:.1f}°C"
            return "Temp: N/A"
        except Exception:
            return "Temp: Error"

class HazardDetectionGUI:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Multi Hazard Detection System")
        self.root.geometry("1440x900")
        
        # Set color theme
        ctk.set_appearance_mode("dark")
        self.root.configure(fg_color="#0A0A0A")
        
        # Initialize system monitor
        self.system_monitor = SystemMonitor()
        
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
        
        # Create screenshots directory
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.create_gui()
        self.start_monitoring()
        
    def create_gui(self):
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="#0A0A0A")
        self.main_container.pack(fill="both", expand=True)
        
        # Create header
        self.create_header()
        
        # Create main content area with three columns
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="#0A0A0A")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create three columns
        self.create_left_sidebar()
        self.create_main_content()
        self.create_right_sidebar()
        
        # Create footer
        self.create_footer()
        
    def create_header(self):
        header = ctk.CTkFrame(self.main_container, fg_color="#101010", height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=20)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="💫 Multi Hazard Detection System",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(side="left")
        
        # System monitoring frame
        monitoring_frame = ctk.CTkFrame(header, fg_color="transparent")
        monitoring_frame.pack(side="right", padx=20)
        
        # Clock
        self.clock_label = ctk.CTkLabel(
            monitoring_frame,
            text="00:00:00",
            font=("Helvetica", 16),
            text_color="#4CAF50"
        )
        self.clock_label.pack(side="left", padx=(0, 20))
        
        # RAM Usage
        self.ram_label = ctk.CTkLabel(
            monitoring_frame,
            text="RAM: ---%",
            font=("Helvetica", 16),
            text_color="#2196F3"
        )
        self.ram_label.pack(side="left", padx=(0, 20))
        
        # GPU Usage
        self.gpu_label = ctk.CTkLabel(
            monitoring_frame,
            text="GPU: ---%",
            font=("Helvetica", 16),
            text_color="#FF9800"
        )
        self.gpu_label.pack(side="left", padx=(0, 20))
        
        # Temperature
        self.temp_label = ctk.CTkLabel(
            monitoring_frame,
            text="CPU: ---°C",
            font=("Helvetica", 16),
            text_color="#F44336"
        )
        self.temp_label.pack(side="left")
    
    def start_monitoring(self):
        def update_monitoring():
            # Update clock
            current_time = time.strftime("%H:%M:%S")
            self.clock_label.configure(text=current_time)
            
            # Update system metrics
            self.ram_label.configure(text=self.system_monitor.get_ram_usage())
            self.gpu_label.configure(text=self.system_monitor.get_gpu_usage())
            self.temp_label.configure(text=self.system_monitor.get_cpu_temp())
            
            # Schedule next update
            self.root.after(1000, update_monitoring)
        
        # Start the monitoring loop
        update_monitoring()
        
    def create_left_sidebar(self):
        self.left_sidebar = ctk.CTkFrame(self.content_area, fg_color="#151515", width=250)
        self.left_sidebar.pack(side="left", fill="y", padx=(0, 5))
        self.left_sidebar.pack_propagate(False)
        
        # Video source controls
        source_frame = ctk.CTkFrame(self.left_sidebar, fg_color="#202020")
        source_frame.pack(fill="x", padx=10, pady=10)
        
        source_title = ctk.CTkLabel(
            source_frame,
            text="Video Source",
            font=("Helvetica", 14, "bold"),
            text_color="#FFFFFF"
        )
        source_title.pack(pady=5)
        
        self.source_button = ctk.CTkButton(
            source_frame,
            text="Select Video File",
            command=self.select_video_source,
            fg_color="#303030",
            hover_color="#404040"
        )
        self.source_button.pack(fill="x", padx=10, pady=5)
        
        self.source_label = ctk.CTkLabel(
            source_frame,
            text="No file selected",
            text_color="#AAAAAA"
        )
        self.source_label.pack(pady=5)
        
        # Video controls
        controls_frame = ctk.CTkFrame(self.left_sidebar, fg_color="#202020")
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        controls_title = ctk.CTkLabel(
            controls_frame,
            text="Video Controls",
            font=("Helvetica", 14, "bold"),
            text_color="#FFFFFF"
        )
        controls_title.pack(pady=5)
        
        self.play_pause_btn = ctk.CTkButton(
            controls_frame,
            text="Play Video",
            command=self.toggle_video,
            fg_color="#252525",
            hover_color="#353535"
        )
        self.play_pause_btn.pack(pady=5, padx=10, fill="x")
        
        self.restart_btn = ctk.CTkButton(
            controls_frame,
            text="Restart Video",
            command=self.restart_video,
            fg_color="#252525",
            hover_color="#353535"
        )
        self.restart_btn.pack(pady=5, padx=10, fill="x")
        
        self.screenshot_btn = ctk.CTkButton(
            controls_frame,
            text="Take Screenshot",
            command=self.take_screenshot,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A"
        )
        self.screenshot_btn.pack(pady=5, padx=10, fill="x")
        
    def create_main_content(self):
        self.main_content = ctk.CTkFrame(self.content_area, fg_color="#080808")
        self.main_content.pack(side="left", fill="both", expand=True, padx=5)
        
        # Video display
        self.video_label = ctk.CTkLabel(
            self.main_content,
            text="No video loaded",
            text_color="#CCCCCC"
        )
        self.video_label.pack(fill="both", expand=True)
        
    def create_right_sidebar(self):
        self.right_sidebar = ctk.CTkFrame(self.content_area, fg_color="#151515", width=250)
        self.right_sidebar.pack(side="right", fill="y", padx=(5, 0))
        self.right_sidebar.pack_propagate(False)
        
        # Detection modes
        modes_frame = ctk.CTkFrame(self.right_sidebar, fg_color="#202020")
        modes_frame.pack(fill="x", padx=10, pady=10)
        
        modes_title = ctk.CTkLabel(
            modes_frame,
            text="Detection Modes",
            font=("Helvetica", 14, "bold"),
            text_color="#FFFFFF"
        )
        modes_title.pack(pady=10)
        
        modes = [
            ("👥 Crowd Detection", "crowd"),
            ("🔥 Fire Detection", "fire"),
            ("🚬 Smoking Detection", "smoking"),
            ("🚗 Vehicle Detection", "vehicle"),
            ("⚠️ Weapon Detection", "weapon")
        ]
        
        for mode_text, mode_value in modes:
            btn = ctk.CTkButton(
                modes_frame,
                text=mode_text,
                command=lambda m=mode_value: self.set_detection_mode(m),
                # fg_color="#303030",
                # hover_color="#404040"
            )
            btn.pack(pady=5, padx=10, fill="x")
            
        # Detection control
        self.detection_btn = ctk.CTkButton(
            self.right_sidebar,
            text="Start Detection",
            command=self.toggle_detection,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.detection_btn.pack(pady=20, padx=20, fill="x")
        
    def create_footer(self):
        footer = ctk.CTkFrame(self.main_container, fg_color="#101010", height=30)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        footer.pack_propagate(False)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            footer,
            text="In-Development Deep Learning Model",
            text_color="#808080"
        )
        self.status_label.pack(side="left", padx=20)
        
        # Creator credit
        credit_label = ctk.CTkLabel(
            footer,
            text="Created by: Yash Raj Suman",
            font=("Helvetica", 12),
            text_color="#808080"
        )
        credit_label.pack(side="right", padx=20)
        
    def start_clock_update(self):
        def update_clock():
            current_time = time.strftime("%H:%M:%S")
            self.clock_label.configure(text=current_time)
            self.root.after(1000, update_clock)
        update_clock()
        
    def update_status(self, message):
        self.status_label.configure(text=message)
    
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
    

    # [Previous methods remain the same: select_video_source, set_detection_mode, 
    # toggle_detection, toggle_video, start_video, pause_video, restart_video, 
    # take_screenshot, process_video]

    def run(self):
        self.root.mainloop()

def main():
    app = HazardDetectionGUI()
    app.run()

if __name__ == "__main__":
    main()