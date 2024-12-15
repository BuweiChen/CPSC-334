import requests

# Replace with the ESP32's IP address
esp32_ip = "192.168.4.1"
port = 80


def send_command(pan, tilt, shoot, laser, motor):
    command = f"P{pan}T{tilt}S{shoot}L{laser}M{motor}"
    url = f"http://{esp32_ip}:{port}/?{command}"
    response = requests.get(url)
    print(f"Sent: {command}, Response: {response.text}")


# Example usage
send_command(120, 110, 1, 0, 0)  # Pan 90°, Tilt 45°, Shoot, Laser on


# -90
# 90

# 30
# 210

# 90
# 155

# 90
# 105
