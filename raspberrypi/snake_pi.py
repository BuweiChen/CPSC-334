import RPi.GPIO as GPIO
import smbus
import time

address = 0x48
bus = smbus.SMBus(1)
cmd=0x40

BUTTON_PIN = 16
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# button input
time.sleep(0.01)
button_state = GPIO.input(BUTTON_PIN)
if button_state == GPIO.LOW:
    print("Button pressed")
    
