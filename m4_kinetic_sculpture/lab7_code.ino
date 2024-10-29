#include <Stepper.h>
#include <ESP32Servo.h>

// ULN2003 Motor Driver Pins
#define IN1 19
#define IN2 18
#define IN3 5
#define IN4 17
#define IN_SERVO 13

const int stepsPerRevolution = 1024;  // change this to fit the number of steps per revolution

// initialize the stepper library
Stepper myStepper(stepsPerRevolution, IN1, IN3, IN2, IN4);

Servo servo1;


int stepper_step = 0;
int servo_deg = 0;

void setup() {
  // set the speed at 5 rpm
  myStepper.setSpeed(40);
  // initialize the serial port
  Serial.begin(115200);
  servo1.attach(IN_SERVO);
}

void loop() {
  // // step one revolution in one direction:
  // Serial.println("clockwise");
  // myStepper.step(stepsPerRevolution);
  // delay(1000);

  // // step one revolution in the other direction:
  // Serial.println("counterclockwise");
  // myStepper.step(-stepsPerRevolution);
  // delay(1000);

  // for(int posDegrees = 0; posDegrees <= 180; posDegrees++) {
  //   servo1.write(posDegrees);
  //   Serial.println(posDegrees);
  //   delay(20);
  // }

  // for(int posDegrees = 180; posDegrees >= 0; posDegrees--) {
  //   servo1.write(posDegrees);
  //   Serial.println(posDegrees);
  //   delay(20);
  // }

  int stepper_update = stepsPerRevolution/64;

  myStepper.step(stepper_update);
  stepper_step += stepper_update;
  Serial.println("stepper_step");
  Serial.println(stepper_step);
  
  if (stepper_step != 0 && stepper_step % 2048 == 0) {
    servo_deg += 10;
    servo1.write(servo_deg);
  }

  if (servo_deg == 180) {
    servo_deg = 0;
    servo1.write(servo_deg);
  }

  Serial.println("servo_deg");
  Serial.println(servo_deg);
}