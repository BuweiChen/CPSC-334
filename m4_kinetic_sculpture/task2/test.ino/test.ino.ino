#include <Stepper.h>
#include <ESP32Servo.h>

#define IN_SERVO 13

Servo servo1;

int servo_deg = 0;

void setup() {
  Serial.begin(115200);
  servo1.attach(IN_SERVO);
}

void loop() {
  servo_deg += 10;
  servo1.write(servo_deg);

  if (servo_deg == 180) {
    servo_deg = 0;
    servo1.write(servo_deg);
  }
}