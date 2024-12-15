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
        self.root.geometry("400x500")
        self.cursor_tracking = False
        # self.current_mood = "Neutral"
        self.current_mood = "Happy"

        # Mood system variables
        self.angry_chance = 0
        self.sad_chance = 10
        self.last_command_time = time.time()
        self.commands_blocked = False

        # Variables for state
        self.motor_enabled = BooleanVar(value=False)
        self.laser_enabled = BooleanVar(value=False)
        self.speed_value = IntVar(value=0)
        self.pan_value = IntVar(value=120)
        self.tilt_value = IntVar(value=90)

        # Create UI components
        self.create_widgets()
        self.start_threads()

        # Bind keyboard events
        self.root.bind("<m>", lambda event: self.toggle_motor())
        self.root.bind("<l>", lambda event: self.toggle_laser())
        self.root.bind("<Button-1>", lambda event: self.shoot_action())
        self.root.bind("<Escape>", lambda event: self.toggle_cursor_tracking(False))

        self.update_mood_display()

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
            self.root, text=f"Mood: {self.current_mood}", fg="blue", font=("Arial", 10)
        )
        self.mood_label.place(x=10, y=10)

        # Dance Button
        self.dance_button = tk.Button(
            self.root, text="Click to Dance", command=self.dance_action
        )
        self.dance_button.place(x=250, y=270)
        self.dance_button.place_forget()

        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="green")
        self.status_label.place(x=10, y=30)

    # --- Mood System ---
    def start_threads(self):
        # threading.Thread(target=self.mood_loop, daemon=True).start()
        # threading.Thread(target=self.increase_sad_chance, daemon=True).start()
        pass

    def mood_loop(self):
        while True:
            time.sleep(random.randint(5, 15))
            self.determine_mood()

    def increase_sad_chance(self):
        while True:
            time.sleep(5)
            if time.time() - self.last_command_time > 5:
                self.sad_chance += 10

    def determine_mood(self):
        if self.commands_blocked:
            return  # Skip if actions are blocked
        if random.randint(1, 100) <= self.angry_chance:
            self.current_mood = "Angry"
            self.perform_angry_action()
        elif random.randint(1, 100) <= self.sad_chance:
            self.current_mood = "Sad"
        else:
            self.current_mood = random.choice(["Neutral", "Happy"])

        self.update_mood_display()

    def update_mood_display(self):
        self.mood_label.config(text=f"Mood: {self.current_mood}")
        if self.current_mood == "Happy":
            self.dance_button.place(x=250, y=270)
        else:
            self.dance_button.place_forget()

    def perform_angry_action(self):
        self.commands_blocked = True
        self.status_label.config(text="Angry! Blocking Commands...", fg="red")
        random_pan = self.pan_value.get() + random.choice([-10, 10])
        random_tilt = self.tilt_value.get() + random.choice([-10, 10])
        self.send_command(f"P{random_pan}T{random_tilt}")
        self.send_command("M1")
        time.sleep(2)
        self.send_command("M0")
        self.commands_blocked = False

    # --- Event Handlers ---
    def toggle_motor(self):
        if self.commands_blocked:
            return
        self.motor_enabled.set(not self.motor_enabled.get())
        state = 255 if self.motor_enabled.get() else 0
        self.speed_value.set(state)
        self.motor_button.config(text=f"Motor: {'On' if state else 'Off'}")
        self.angry_chance += 1
        self.send_command(f"M{int(self.motor_enabled.get())}")

    def toggle_laser(self):
        if self.commands_blocked:
            return
        self.laser_enabled.set(not self.laser_enabled.get())
        self.laser_button.config(
            text=f"Laser: {'On' if self.laser_enabled.get() else 'Off'}"
        )
        self.send_command(f"L{int(self.laser_enabled.get())}")

    def shoot_action(self):
        if self.commands_blocked:
            return
        if self.current_mood == "Sad":
            self.shake_head()
            return
        self.send_command("S1")
        self.angry_chance += 4

    def dance_action(self):
        self.commands_blocked = True
        dance_moves = [
            (90, 130),
            (70, 120),
            (50, 140),
            (70, 120),
            (90, 140),
            (110, 120),
            (130, 140),
            (110, 120),
            (90, 130),
            (150, 130),
            (190, 130),
            (150, 130),
            (90, 130),
            (50, 130),
            (10, 130),
            (50, 130),
            (90, 130),
        ]
        for x, y in dance_moves:
            self.send_command(f"P{x}T{y}")
            time.sleep(0.5)
        self.commands_blocked = False

    def shake_head(self):
        self.commands_blocked = True
        head_shake = [(90, 140), (80, 140), (100, 140), (80, 140), (90, 140)]
        for x, y in head_shake:
            self.send_command(f"P{x}T{y}")
            time.sleep(0.5)
        self.commands_blocked = False

    def toggle_cursor_tracking(self, state=None):
        self.cursor_tracking = state if state is not None else not self.cursor_tracking
        self.cursor_track_button.config(
            text=f"Cursor Track: {'On' if self.cursor_tracking else 'Off'}"
        )

    def cursor_motion(self, event):
        if self.commands_blocked or not self.cursor_tracking:
            return
        x = int(event.x / self.aim_area.winfo_width() * 180)
        y = int(event.y / self.aim_area.winfo_height() * 180) + 30
        x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
        self.pan_value.set(x)
        self.tilt_value.set(y)
        self.send_command(f"P{x}T{y}")

    def click_to_aim(self, event):
        if self.commands_blocked:
            return
        x = int(event.x / self.aim_area.winfo_width() * 180)
        y = int(event.y / self.aim_area.winfo_height() * 180) + 30
        x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
        self.pan_value.set(x)
        self.tilt_value.set(y)
        self.send_command(f"P{x}T{y}")

    def send_command(self, command):
        try:
            url = f"http://{ESP32_IP}:{PORT}/?{command}"
            requests.get(url)
            self.last_command_time = time.time()
        except Exception as e:
            print(f"Command Error: {e}")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TurretControlApp(root)
    root.mainloop()
