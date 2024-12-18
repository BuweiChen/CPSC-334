# Laser Turret v1.0

A turret that shoots lasers, controlled wirelessly from your laptop :) Module 4 submission for CPSC 334 (Creative Embedded Systems).

Project Video: https://youtu.be/RGZOuUn0OxQ

Project Blog: https://www.notion.so/Laser-Turret-v1-0-1413781e92768074bc29f9189e029282 

## Code Walkthrough

Essentially, we start a server on the ESP32 controlling the turret that listens for commands and executes them accordingly; and on the laptop side we have a python script that connects to the server and sends commands according to which keystrokes it detects from the user.

### Turret Code

```c
#include <ESP32Servo.h>
#include <WiFi.h>

#define HORIZ_SERVO 12 // GPIO for horizontal servo
#define VERT_SERVO 13  // GPIO for vertical servo
#define LASER_SERVO 14 // GPIO for laser trigger servo

Servo horizontalServo;
Servo verticalServo;
Servo laserTriggerServo;

// Initial servo angles
int horizontalAngle = 90;
int verticalAngle = 90;
int laserAngle = 90;

// Movement step size
const int stepSize = 5;   // Smaller steps for smooth movement
const int minAngle = 0;   // Minimum angle
const int maxAngle = 180; // Maximum angle

// Wi-Fi credentials
const char* ssid = "yale wireless";
const char* password = "";

// Server
WiFiServer server(80);

// Current movement state
String currentCommand = "";

void setup() {
  Serial.begin(115200);

  // Attach servos
  horizontalServo.attach(HORIZ_SERVO);
  verticalServo.attach(VERT_SERVO);
  laserTriggerServo.attach(LASER_SERVO);

  // Set initial positions
  horizontalServo.write(horizontalAngle);
  verticalServo.write(verticalAngle);
  laserTriggerServo.write(laserAngle);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
  Serial.println(WiFi.localIP());

  // Start server
  server.begin();
  Serial.println("Server started");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String request = client.readStringUntil('\r'); // Read the HTTP request line
    client.flush();

    // Extract command from the HTTP GET request
    if (request.indexOf("command:") > -1) {
      int startIdx = request.indexOf("command:") + 8;
      currentCommand = request.substring(startIdx, startIdx + 1);
      Serial.println("Received command: " + currentCommand);
    }

    // Send HTTP response
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println("OK");
    client.stop();
  }

  // Perform movement based on current command
  if (currentCommand == "w") {
    verticalAngle = constrain(verticalAngle - stepSize, minAngle, maxAngle);
    verticalServo.write(verticalAngle);
  } else if (currentCommand == "s") {
    verticalAngle = constrain(verticalAngle + stepSize, minAngle, maxAngle);
    verticalServo.write(verticalAngle);
  } else if (currentCommand == "a") {
    horizontalAngle = constrain(horizontalAngle + stepSize, minAngle, maxAngle);
    horizontalServo.write(horizontalAngle);
  } else if (currentCommand == "d") {
    horizontalAngle = constrain(horizontalAngle - stepSize, minAngle, maxAngle);
    horizontalServo.write(horizontalAngle);
  } else if (currentCommand == "f") {
    laserTriggerServo.write(laserAngle + 15);
  }

  if (currentCommand != "f") {
    laserTriggerServo.write(laserAngle);
  }

  delay(50); // Adjust speed of movement
}
```

### Controller Code

```python
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
```
