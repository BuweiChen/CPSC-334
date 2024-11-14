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
