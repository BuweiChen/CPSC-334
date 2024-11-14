import requests
from pynput import keyboard
import threading

# ESP32 server details
ESP32_IP = "10.67.73.44"
PORT = 80

# State for currently pressed key
current_key = None
stop_thread = False


def send_command(command):
    try:
        url = f"http://{ESP32_IP}:{PORT}/?command:{command}"
        response = requests.get(url, timeout=1)
        if response.status_code != 200:
            print(f"ESP32 error: {response.status_code}")
    except Exception as e:
        print(f"Failed to send command: {e}")


def command_sender():
    global current_key, stop_thread
    while not stop_thread:
        if current_key:
            send_command(current_key)
        else:
            send_command("")  # Stop if no key is pressed
        threading.Event().wait(0.1)  # Adjust for desired responsiveness


# Start the sender thread
threading.Thread(target=command_sender, daemon=True).start()


def on_press(key):
    global current_key
    try:
        if key == keyboard.Key.space:
            current_key = "fire"
        elif key.char in ["w", "a", "s", "d"]:
            current_key = key.char
    except AttributeError:
        pass


def on_release(key):
    global current_key
    if key in [keyboard.Key.space] or (
        hasattr(key, "char") and key.char in ["w", "a", "s", "d"]
    ):
        current_key = None  # Stop sending command


# Listen for keyboard inputs
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    stop_thread = True
    print("Exiting...")
