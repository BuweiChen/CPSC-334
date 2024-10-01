import serial
import time

# Replace 'COM3' with your port on Windows, or '/dev/ttyUSB0' on Linux/macOS
ser = serial.Serial("/dev/tty.usbserial-1130", 115200, timeout=1)
ser.flush()

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()
        print(line)  # Print the data received from ESP32
