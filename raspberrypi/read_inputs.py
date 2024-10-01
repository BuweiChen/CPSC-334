"""
from machine import Pin, ADC
import time

# Initialize ADCs for X and Y axes (for the joystick)
x_axis = ADC(Pin(34))  # Pin 34 for X-axis
y_axis = ADC(Pin(35))  # Pin 35 for Y-axis
x_axis.width(ADC.WIDTH_10BIT)
x_axis.atten(ADC.ATTN_11DB)
y_axis.width(ADC.WIDTH_10BIT)
y_axis.atten(ADC.ATTN_11DB)

# Initialize button on GPIO 14 and switch on GPIO 27
button = Pin(14, Pin.IN, Pin.PULL_UP)  # Button is active-low, use pull-up
switch = Pin(27, Pin.IN, Pin.PULL_UP)  # Switch is active-low, use pull-up

while True:
    # Read analog values from the joystick
    x_value = x_axis.read()  # Read X-axis value
    y_value = y_axis.read()  # Read Y-axis value

    # Read the button and switch states
    button_state = button.value()  # 0 when pressed, 1 when not pressed
    switch_state = switch.value()  # 0 when pressed, 1 when not pressed

    # Print joystick, button, and switch values
    print("X-axis: {}, Y-axis: {}".format(x_value, y_value))
    print("Button pressed: {}".format(button_state == 0))  # True when pressed
    print("Switch on: {}".format(switch_state == 0))  # True when switched on

    time.sleep(0.1)

"""


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

while True:
    # Read the button and switch
    button_state = button.value()
    switch_state = switch.value()

    # Read joystick values
    x_value = x_axis.read()
    y_value = y_axis.read()

    # Create a string to send over UART
    data = "X:{} Y:{} Button:{} Switch:{}\n".format(x_value, y_value, button_state, switch_state)

    # Send the data over UART
    print(data)
    uart.write(data)

    time.sleep(0.1)
