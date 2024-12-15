import serial

# Connect to the ESP32 Bluetooth Serial Port
esp32_port = "/dev/ttyUSB0"  # Replace with your port (e.g., COM3 on Windows)
baud_rate = 9600
bt_serial = serial.Serial(esp32_port, baud_rate)


def send_command(pan, tilt, shoot, laser):
    # Format the command
    command = f"P{pan}T{tilt}S{shoot}L{laser}\n"
    bt_serial.write(command.encode())
    print(f"Sent: {command}")


# Example usage
send_command(90, 45, 0, 1)  # Pan to 90, Tilt to 45, no shoot, laser on
