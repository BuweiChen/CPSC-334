# ESP32 code, micropython

from machine import Pin, ADC, UART
import time

# Initialize UART (baudrate of 9600, pins are default for UART0 on ESP32)
uart = UART(1, baudrate=115200)

# Initialize button and switch
button = Pin(14, Pin.IN, Pin.PULL_UP)  # Button on GPIO 14
switch = Pin(27, Pin.IN, Pin.PULL_UP)  # Switch on GPIO 27

# Initialize joystick
x_axis = ADC(Pin(34))  # X-axis
y_axis = ADC(Pin(35))  # Y-axis
x_axis.width(ADC.WIDTH_10BIT)  # 10-bit width (0-1023)
y_axis.width(ADC.WIDTH_10BIT)
x_axis.atten(ADC.ATTN_11DB)
y_axis.atten(ADC.ATTN_11DB)

while True:
    # Read the button and switch
    button_state = button.value()
    switch_state = switch.value()

    # Read joystick values
    x_value = x_axis.read()
    y_value = y_axis.read()

    # Create a string to send over UART
    data = "{},{},{},{}\n".format(x_value, y_value, button_state, switch_state)

    # Send the data over UART
    print(data)
    # uart.write(data)

    time.sleep(0.1)
