import tkinter as tk
from tkinter import IntVar, BooleanVar, Label
import requests

# ESP32 Server Configuration
ESP32_IP = "192.168.4.1"
PORT = 80


class TurretControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Turret Control Interface")
        self.root.geometry("400x400")
        self.cursor_tracking = False

        # Variables for state
        self.motor_enabled = BooleanVar(value=False)
        self.laser_enabled = BooleanVar(value=False)
        self.speed_value = IntVar(value=0)
        self.pan_value = IntVar(value=120)
        self.tilt_value = IntVar(value=90)

        # Create UI components
        self.create_widgets()

        # Bind keyboard events
        self.root.bind(
            "<m>", lambda event: self.toggle_motor() if self.cursor_tracking else None
        )
        self.root.bind(
            "<l>", lambda event: self.toggle_laser() if self.cursor_tracking else None
        )
        self.root.bind(
            "<Button-1>",
            lambda event: self.shoot_action() if self.cursor_tracking else None,
        )  # Left Click
        self.root.bind("<Escape>", lambda event: self.toggle_cursor_tracking(False))

    def create_widgets(self):
        # Aim Area
        self.aim_area = tk.Canvas(self.root, width=200, height=200, bg="lightgrey")
        self.aim_area.place(x=10, y=50)
        self.aim_area.bind("<Motion>", self.cursor_motion)

        # Motor Toggle
        self.motor_button = tk.Button(
            self.root, text="Motor: Off", command=self.toggle_motor
        )
        self.motor_button.place(x=250, y=10)

        # Shoot Toggle
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

        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="green")
        self.status_label.place(x=10, y=10)

    # --- Command Sending Function ---
    def send_command(self, command):
        try:
            url = f"http://{ESP32_IP}:{PORT}/?{command}"
            requests.get(url)
            self.status_label.config(text="Command Sent", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

    # --- Event Handlers ---
    def toggle_motor(self):
        self.motor_enabled.set(not self.motor_enabled.get())
        state = 255 if self.motor_enabled.get() else 0
        self.speed_value.set(state)
        self.motor_button.config(text=f"Motor: {'On' if state else 'Off'}")
        self.send_command(f"M{int(self.motor_enabled.get())}")

    def toggle_laser(self):
        self.laser_enabled.set(not self.laser_enabled.get())
        self.laser_button.config(
            text=f"Laser: {'On' if self.laser_enabled.get() else 'Off'}"
        )
        self.send_command(f"L{int(self.laser_enabled.get())}")

    def shoot_action(self):
        self.send_command("S1")
        self.status_label.config(text="Shooting", fg="orange")

    def toggle_cursor_tracking(self, state=None):
        if state is not None:
            self.cursor_tracking = state
        else:
            self.cursor_tracking = not self.cursor_tracking
        self.cursor_track_button.config(
            text=f"Cursor Track: {'On' if self.cursor_tracking else 'Off'}"
        )
        self.status_label.config(
            text="Cursor Tracking: On"
            if self.cursor_tracking
            else "Cursor Tracking: Off",
            fg="purple",
        )

    def cursor_motion(self, event):
        if self.cursor_tracking:
            # Map cursor position to pan and tilt values
            x = int(event.x / self.aim_area.winfo_width() * 180)
            y = int(event.y / self.aim_area.winfo_height() * 180) + 30

            # Constrain values
            x = 180 - max(0, min(180, x))
            y = max(30, min(210, y))

            # Update Pan and Tilt
            self.pan_value.set(x)
            self.tilt_value.set(y)
            self.send_command(f"P{x}T{y}")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TurretControlApp(root)
    root.mainloop()
