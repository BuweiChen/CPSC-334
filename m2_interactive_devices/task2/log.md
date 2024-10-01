9/29/24

#### Getting the esp32 to communicate with computer via python

The easiest way to have esp32 communicate with computer via python is micropython.
I followed the installation process here: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html.

The first steps involved installing esptool and erasing/flashing the micropython firmware onto the esp32.
I had trouble looking for the port the esp32 is connected to.

Turned out it looked something like `--port /dev/tty.usbserial-1130`

It was also weirdly difficult to find the correct firmware to flash, since all the instructions points to something that looks like `esp32-20210902-v1.17.bin`, but even the official website takes you to download something like `micropython-1.23.0.tar.xz` which is a folder that doesn't contain anything that remotely resembles the `.bin` file. I found the one to download eventually here https://micropython.org/download/ESP32_GENERIC/

On the code side, I tried to make vscode work with PyMakr. It was terrible. So I switched to Thonny (the name did not give me confidence but apparently there are a lot of guides on it integrating with esp32. Sorry, I do judge a book by its cover).

Found some helpful code/instructions from https://randomnerdtutorials.com/esp32-esp8266-analog-readings-micropython/. Needed to manually set the interpreter to be the esp32 through options > interpreter.

Writing the code was straightforward. The library for reading inputs is nice and simple. Took some pictures/videos once I got the joystick/switch/button to work. Onto the game portion then.

First thing to do here is to read the input being collected from esp32 into the program that actually runs the game. So I changed the `print` statements into `write`s.

There's another layer here, which is I don't want to develop on a raspberry pi, so I'm trying to get as much development done before I'm forced to configure everything to work with a pi. Turns out that means we just stick with `print` statements and that's fine.

On the game code side, we use the pyserial library to fetch the data with a block of relatively simple code

```python
import serial

ser = serial.Serial("/dev/tty.usbserial-1130", 115200, timeout=1)
ser.flush()

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()
        print(line)  # Print the data received from ESP32
```

The code was behaving weirdly when I added a `time.sleep` command at the end of the loop. Which makes sense, since we are reading the lines slower than they are coming in.

After some brief tweaking of the esp32 code. Here's the presently working version:

```python
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
    data = "X:{} Y:{} Button:{} Switch:{}\n".format(x_value, y_value, button_state, switch_state)

    # Send the data over UART
    print(data)
    #uart.write(data)

    time.sleep(0.1)
```

These two lines were surprisingly crucial for the esp32 to output correctly, otherwise neutral would be 1023 and moving the joystick beyond that wouldn't have any effect. Curious.

```python
x_axis.atten(ADC.ATTN_11DB)
y_axis.atten(ADC.ATTN_11DB)
```

Writing the game code is rather straightforward since I've implemented the snake game across different platforms/languages multiple times. However, there are some interesting tid-bits to note.

1. When reading handling user input, the traditional switch statement won't necessarily work

```python
if abs(x_value - 457) > 10 or abs(y_value - 457) > 10:
    if x_value > 457 + 10:
        active_snake.direction = (1, 0)  # Move right
    elif x_value < 457 - 10:
        active_snake.direction = (-1, 0)  # Move left
    elif y_value > 457 + 10:
        active_snake.direction = (0, 1)  # Move down
    elif y_value < 457 - 10:
        active_snake.direction = (0, -1)  # Move up
```

because the hierarchy implies that certain inputs takes priority over others. For example, consider the case here when `x = 300, y = 0`. Intuitively, we know we should be reading an `up` direction since the `y` is further away from being neutral than `x`, but that's not how the program behaves.

So instead, we implement something like this

```python
# Define the neutral region
neutral = 457
neutral_tolerance = 10
max_deviation = 1023 - neutral

# Calculate deviation percentages for x and y
x_deviation = abs(x_value - neutral) / max_deviation
y_deviation = abs(y_value - neutral) / max_deviation

# If the joystick is outside the neutral zone, choose the direction with greater deviation
if max(x_deviation, y_deviation) > neutral_tolerance / max_deviation:
    if x_deviation > y_deviation:  # x-axis movement
        if x_value > neutral + neutral_tolerance and active_snake.direction != (
            -1,
            0,
        ):
            active_snake.direction = (1, 0)  # Move right
        elif (
            x_value < neutral - neutral_tolerance
            and active_snake.direction != (1, 0)
        ):
            active_snake.direction = (-1, 0)  # Move left
    else:  # y-axis movement
        if y_value > neutral + neutral_tolerance and active_snake.direction != (
            0,
            -1,
        ):
            active_snake.direction = (0, 1)  # Move down
        elif (
            y_value < neutral - neutral_tolerance
            and active_snake.direction != (0, 1)
        ):
            active_snake.direction = (0, -1)  # Move up
```

You might have noticed already, we also don't want the snake to turn 180 degrees and instantly kills itself. The design is very human.

Weird bug where when the snake shoots another snake from behind, only the first block disappears.