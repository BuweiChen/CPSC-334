import tkinter as tk
from tkinter import IntVar, BooleanVar, Label
import requests
import random
import threading
import time

# ESP32 Server Configuration
ESP32_IP = "192.168.4.1"
PORT = 80


class TurretControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Turret Control Interface")
        self.root.geometry("400x450")
        self.cursor_tracking = False
        self.current_mood = "Neutral"

        # Mood system variables
        self.angry_chance = 0
        self.sad_chance = 10
        self.last_command_time = time.time()

        # Variables for state
        self.motor_enabled = BooleanVar(value=False)
        self.laser_enabled = BooleanVar(value=False)
        self.speed_value = IntVar(value=0)
        self.pan_value = IntVar(value=120)
        self.tilt_value = IntVar(value=90)

        # Create UI components
        self.create_widgets()
        self.update_mood_loop()

        # Bind keyboard events
        self.root.bind("<m>", lambda event: self.toggle_motor())
        self.root.bind("<l>", lambda event: self.toggle_laser())
        self.root.bind("<Button-1>", lambda event: self.shoot_action())
        self.root.bind("<Escape>", lambda event: self.toggle_cursor_tracking(False))

    # --- UI Creation ---
    def create_widgets(self):
        # Aim Area
        self.aim_area = tk.Canvas(self.root, width=200, height=200, bg="lightgrey")
        self.aim_area.place(x=10, y=50)
        self.aim_area.bind("<Motion>", self.cursor_motion)
        self.aim_area.bind("<Button-1>", self.click_to_aim)

        # Motor Toggle
        self.motor_button = tk.Button(
            self.root, text="Motor: Off", command=self.toggle_motor
        )
        self.motor_button.place(x=250, y=10)

        # Shoot Button
        self.shoot_button = tk.Button(
            self.root, text="Shoot", command=self.shoot_action
        )
        self.shoot_button.place(x=250, y=50)

        # Pan, Tilt, and Speed Values
        Label(self.root, text="Pan:").place(x=250, y=90)
        Label(self.root, textvariable=self.pan_value).place(x=300, y=90)

        Label(self.root, text="Tilt:").place(x=250, y=120)
        Label(self.root, textvariable=self.tilt_value).place(x=300, y=120)

        Label(self.root, text="Speed:").place(x=250, y=150)
        Label(self.root, textvariable=self.speed_value).place(x=300, y=150)

        # Laser Toggle
        self.laser_button = tk.Button(
            self.root, text="Laser: Off", command=self.toggle_laser
        )
        self.laser_button.place(x=250, y=190)

        # Cursor Track Toggle
        self.cursor_track_button = tk.Button(
            self.root, text="Cursor Track: Off", command=self.toggle_cursor_tracking
        )
        self.cursor_track_button.place(x=250, y=230)

        # Mood Display
        self.mood_label = Label(
            self.root, text="Mood: Neutral", fg="blue", font=("Arial", 10)
        )
        self.mood_label.place(x=10, y=10)

        # Dance Button (Hidden until Happy mood)
        self.dance_button = tk.Button(
            self.root, text="Click to Dance", command=self.dance_action
        )
        self.dance_button.place(x=250, y=270)
        self.dance_button.place_forget()

        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="green")
        self.status_label.place(x=10, y=30)

    # --- Command Sending Function ---
    def send_command(self, command):
        try:
            url = f"http://{ESP32_IP}:{PORT}/?{command}"
            requests.get(url)
            self.last_command_time = time.time()
            self.status_label.config(text="Command Sent", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

    # --- Mood System ---
    def update_mood_loop(self):
        def mood_loop():
            while True:
                time.sleep(random.randint(5, 15))
                self.determine_mood()
                self.update_mood_display()

        threading.Thread(target=mood_loop, daemon=True).start()

    def determine_mood(self):
        if random.randint(1, 100) <= self.angry_chance:
            self.current_mood = "Angry"
            self.angry_chance = 0  # Reset
        elif random.randint(1, 100) <= self.sad_chance:
            self.current_mood = "Sad"
            self.sad_chance = 10  # Reset
        else:
            self.current_mood = random.choice(["Neutral", "Happy"])

    def update_mood_display(self):
        self.mood_label.config(text=f"Mood: {self.current_mood}")
        if self.current_mood == "Happy":
            self.dance_button.place(x=250, y=270)
        else:
            self.dance_button.place_forget()

    # --- Event Handlers ---
    def toggle_motor(self):
        self.motor_enabled.set(not self.motor_enabled.get())
        state = 255 if self.motor_enabled.get() else 0
        self.speed_value.set(state)
        self.motor_button.config(text=f"Motor: {'On' if state else 'Off'}")
        self.angry_chance += 1
        self.send_command(f"M{int(self.motor_enabled.get())}")

    def toggle_laser(self):
        self.laser_enabled.set(not self.laser_enabled.get())
        self.laser_button.config(
            text=f"Laser: {'On' if self.laser_enabled.get() else 'Off'}"
        )
        self.send_command(f"L{int(self.laser_enabled.get())}")

    def shoot_action(self):
        if self.current_mood == "Sad":
            self.shake_head()
            return
        self.send_command("S1")
        self.status_label.config(text="Shooting", fg="orange")
        self.angry_chance += 4

    def dance_action(self):
        for step in [
            (90, 110),
            (80, 100),
            (70, 120),
            (80, 100),
            (90, 110),
            (100, 100),
            (110, 120),
            (100, 100),
        ]:
            self.send_command(f"P{step[0]}T{step[1]}")
            time.sleep(0.5)

    def shake_head(self):
        for step in [
            ("P90", "T140"),
            ("P80", "T140"),
            ("P100", "T140"),
            ("P80", "T140"),
            ("P90", "T140"),
        ]:
            self.send_command(f"{step[0]}{step[1]}")
            time.sleep(0.5)

    def toggle_cursor_tracking(self, state=None):
        self.cursor_tracking = state if state is not None else not self.cursor_tracking
        self.cursor_track_button.config(
            text=f"Cursor Track: {'On' if self.cursor_tracking else 'Off'}"
        )

    def cursor_motion(self, event):
        if self.cursor_tracking:
            x = int(event.x / self.aim_area.winfo_width() * 180)
            y = int(event.y / self.aim_area.winfo_height() * 180) + 30
            x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
            self.pan_value.set(x)
            self.tilt_value.set(y)
            self.send_command(f"P{x}T{y}")

    def click_to_aim(self, event):
        x = int(event.x / self.aim_area.winfo_width() * 180)
        y = int(event.y / self.aim_area.winfo_height() * 180) + 30
        x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
        self.pan_value.set(x)
        self.tilt_value.set(y)
        self.send_command(f"P{x}T{y}")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TurretControlApp(root)
    root.mainloop()
