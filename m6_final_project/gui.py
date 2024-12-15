import tkinter as tk
from tkinter import IntVar, BooleanVar
import requests

# ESP32 Server Configuration
ESP32_IP = "192.168.4.1"  # Replace with your ESP32 IP
PORT = 80


class TurretControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Turret Control Interface")
        self.root.geometry("400x400")
        self.cursor_tracking = False

        # Variables for state
        self.motor_enabled = BooleanVar(value=False)
        self.pan_value = IntVar(value=120)
        self.tilt_value = IntVar(value=90)
        self.laser_on = BooleanVar(value=False)

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Aim Area
        self.aim_area = tk.Canvas(self.root, width=200, height=200, bg="lightgrey")
        self.aim_area.place(x=10, y=50)
        self.aim_area.bind("<Motion>", self.cursor_motion)

        # Motor checkbox
        self.motor_checkbox = tk.Checkbutton(
            self.root,
            text="Motor",
            variable=self.motor_enabled,
            command=self.toggle_motor,
        )
        self.motor_checkbox.place(x=270, y=10)

        # Speed Button (for customization)
        self.speed_button = tk.Button(
            self.root, text="Speed", command=self.speed_action
        )
        self.speed_button.place(x=320, y=10)

        # Shoot Button
        self.shoot_button = tk.Button(
            self.root, text="Shoot", command=self.shoot_action
        )
        self.shoot_button.place(x=250, y=50)

        # Pan and Tilt Values
        self.pan_label = tk.Label(self.root, text="Pan:")
        self.pan_label.place(x=250, y=90)
        self.pan_display = tk.Label(self.root, textvariable=self.pan_value)
        self.pan_display.place(x=300, y=90)

        self.tilt_label = tk.Label(self.root, text="Tilt:")
        self.tilt_label.place(x=250, y=120)
        self.tilt_display = tk.Label(self.root, textvariable=self.tilt_value)
        self.tilt_display.place(x=300, y=120)

        # Laser Button
        self.laser_button = tk.Button(
            self.root, text="Laser", command=self.toggle_laser
        )
        self.laser_button.place(x=250, y=160)

        # Cursor Track Button
        self.cursor_track_button = tk.Button(
            self.root, text="Cursor Track", command=self.toggle_cursor_tracking
        )
        self.cursor_track_button.place(x=250, y=200)

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
        state = 1 if self.motor_enabled.get() else 0
        self.send_command(f"M{state}")

    def speed_action(self):
        # Placeholder for Speed Button behavior
        self.status_label.config(text="Speed button pressed", fg="blue")

    def shoot_action(self):
        self.send_command("S1")
        self.status_label.config(text="Shooting", fg="orange")

    def toggle_laser(self):
        state = 1 if not self.laser_on.get() else 0
        self.laser_on.set(state)
        self.send_command(f"L{state}")
        self.status_label.config(text="Laser Toggled", fg="blue")

    def toggle_cursor_tracking(self):
        self.cursor_tracking = not self.cursor_tracking
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
