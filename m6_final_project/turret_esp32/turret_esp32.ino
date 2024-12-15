#include <WiFi.h>
#include <ESP32Servo.h>

// Replace with your network credentials
const char *ssid = "ESP32-Turret";     // Wi-Fi SSID
const char *password = "turret123";   // Wi-Fi Password

// Servo setup
Servo pan_servo;
Servo tilt_servo;
Servo shoot_servo;
Servo laser_servo;

const int motorPin = 18;

// Servo limits
const int pan_min = 0, pan_max = 270;
const int tilt_min = 30, tilt_max = 300;
const int shoot_default = 90, shoot_fire = 155; // Shoot: default/rest position and firing position
const int laser_default = 90, laser_on = 105;  // Laser: default/rest position and "on" position

WiFiServer server(80);

void setup() {
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  Serial.print("Wi-Fi Access Point started. IP Address: ");
  Serial.println(WiFi.softAPIP());

  // Attach servos with appropriate PWM settings
  ESP32PWM::allocateTimer(0); // Allocate all PWM timers
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  pan_servo.setPeriodHertz(50);  // Standard 50 Hz servo
  tilt_servo.setPeriodHertz(50);
  shoot_servo.setPeriodHertz(50);
  laser_servo.setPeriodHertz(50);

  pan_servo.attach(25, 500, 2500);
  tilt_servo.attach(26, 500, 2500); 
  shoot_servo.attach(27, 500, 2500); 
  laser_servo.attach(14, 500, 2500);

  // Set servos to default positions
  pan_servo.write(90);   // Center position
  tilt_servo.write(110);  // Center position
  shoot_servo.write(shoot_default);
  laser_servo.write(laser_default);

  pinMode(motorPin, OUTPUT);

  server.begin(); // Start the server
  Serial.println("Server started.");
}

void loop() {
  // Check for incoming client connections
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected.");
    String request = "";

    // Read the client request
    while (client.connected() && client.available()) {
      char c = client.read();
      request += c;
      if (c == '\n') break; // End of HTTP request
    }

    // Parse the command
    if (request.length() > 0) {
      Serial.println(request);
      handleCommand(request);
    }

    // Send a simple response
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println();
    client.println("Command received.");
    client.stop(); // Disconnect the client
    Serial.println("Client disconnected.");
  }
}

void handleCommand(String request) {
  // Extract the part of the request after "/?"
  int startIdx = request.indexOf("/?") + 2; // Find "/?" and move to the start of the command
  int endIdx = request.indexOf(" HTTP");   // Find the end of the command before " HTTP"
  
  if (startIdx > 1 && endIdx > startIdx) { // Ensure valid indices
    String command = request.substring(startIdx, endIdx); // Extract the command part

    // Process the extracted command
    if (command.startsWith("P")) {
      int pan_angle = command.substring(1, command.indexOf('T')).toInt();
      pan_angle = constrain(pan_angle, pan_min, pan_max);
      pan_servo.write(pan_angle);
    }
    if (command.indexOf('T') != -1) {
      int tilt_angle = command.substring(command.indexOf('T') + 1, command.indexOf('S')).toInt();
      tilt_angle = constrain(tilt_angle, tilt_min, tilt_max);
      tilt_servo.write(tilt_angle);
    }
    if (command.indexOf('S') != -1) {
      int shoot = command.substring(command.indexOf('S') + 1, command.indexOf('L')).toInt();
      // shoot_servo.write(shoot);
      if (shoot == 1) {
        shoot_servo.write(shoot_fire);
        delay(200); // Simulate shooting delay
        shoot_servo.write(shoot_default);
      }
    }
    if (command.indexOf('M') != -1) {
      int motor = command.substring(command.indexOf('M') + 1).toInt();
      // laser_servo.write(laser);
      if (motor == 1) {
        analogWrite(motorPin, 255);
      } else {
        analogWrite(motorPin, 0); // Turn laser "off"
      }
    }
    if (command.indexOf('L') != -1) {
      int laser = command.substring(command.indexOf('L') + 1).toInt();
      // laser_servo.write(laser);
      if (laser == 1) {
        laser_servo.write(laser_on); // Turn laser "on"
      } else {
        laser_servo.write(laser_default); // Turn laser "off"
      }
    }
  } else {
    Serial.println("Invalid request format!");
  }
}
