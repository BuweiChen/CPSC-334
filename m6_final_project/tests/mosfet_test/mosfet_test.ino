// Define the pin connected to the MOSFET gate
const int motorPin = 18; // Use a PWM-capable pin

void setup() {
  // Set the motor pin as an output
  pinMode(motorPin, OUTPUT);
}

void loop() {
  // Example: Ramp up the motor speed
  for (int speed = 0; speed <= 255; speed++) {
    analogWrite(motorPin, speed); // Set the motor speed
    delay(10); // Wait for 10 milliseconds
  }

  // Example: Ramp down the motor speed
  for (int speed = 255; speed >= 0; speed--) {
    analogWrite(motorPin, speed); // Set the motor speed
    delay(10); // Wait for 10 milliseconds
  }
}