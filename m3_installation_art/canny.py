import pygame as pg
import os
import socket
import threading

pg.init()

# Screen settings
screen = pg.display.set_mode((800, 600))

# Directory path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Global variables to store distance and heart rate
current_distance = 0.0
current_heartrate = 0
curr_sound_playing = None

# ESP32 server settings
ESP32_IP = "10.67.73.44"
ESP32_PORT = 80

# Preload images and sounds to avoid repetitive loading
images = {
    "canny": [
        pg.transform.scale(
            pg.image.load(os.path.join(dir_path, "media", f"canny{i}.png")), (800, 600)
        )
        for i in range(1, 6)
    ],
    "uncanny": [
        pg.transform.scale(
            pg.image.load(os.path.join(dir_path, "media", f"uncanny{i}.png")),
            (800, 600),
        )
        for i in range(1, 6)
    ],
}
sounds = {
    "canny": [os.path.join(dir_path, "media", f"canny{i}.mp3") for i in range(1, 6)],
    "uncanny": [
        os.path.join(dir_path, "media", f"uncanny{i}.mp3") for i in range(1, 6)
    ],
}

# Lock for thread safety when accessing sensor data
data_lock = threading.Lock()


def get_distance():
    with data_lock:
        return current_distance


def get_heartrate():
    with data_lock:
        return current_heartrate


def update_sensor_data():
    global current_distance, current_heartrate
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ESP32_IP, ESP32_PORT))
            sock.settimeout(2)

            # Receive a single packet of data and decode it
            data = sock.recv(1024).decode("utf-8").strip()
            if data:
                for line in data.splitlines():
                    if "Heart Rate (BPM):" in line:
                        current_heartrate = float(line.split(":")[1].strip())
                    elif "Distance (cm):" in line:
                        current_distance = float(line.split(":")[1].strip())
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        print(f"Connection error: {e}. Retrying next cycle.")


def display_image(image):
    screen.blit(image, (0, 0))


def play_music(music_path):
    pg.mixer.music.load(music_path)
    pg.mixer.music.play(-1, 0.0)


def update_display_and_sound(is_uncanny, dist):
    global curr_sound_playing
    thresholds = [30, 60, 90, 120]

    for i, threshold in enumerate(thresholds):
        if dist < threshold:
            display_image(images["uncanny" if is_uncanny else "canny"][4-i])
            sound_path = sounds["uncanny" if is_uncanny else "canny"][4-i]
            if curr_sound_playing != sound_path:
                play_music(sound_path)
                curr_sound_playing = sound_path
            return

    # Default to the farthest image and sound if no threshold matched
    display_image(images["uncanny" if is_uncanny else "canny"][-1])
    sound_path = sounds["uncanny" if is_uncanny else "canny"][-1]
    if curr_sound_playing != sound_path:
        play_music(sound_path)
        curr_sound_playing = sound_path


# # Run the client in a background thread to constantly update data
# sensor_thread = threading.Thread(target=update_sensor_data)
# sensor_thread.daemon = True
# sensor_thread.start()

clock = pg.time.Clock()
done = False
last_sensor_update = pg.time.get_ticks()
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

    current_time = pg.time.get_ticks()
    if current_time - last_sensor_update >= 500:
        update_sensor_data()
        last_sensor_update = current_time  # Reset the timer
    # Retrieve current sensor data
    dist = get_distance()
    heartrate = get_heartrate()

    print(dist, heartrate)

    # Determine uncanny or canny based on heart rate
    is_uncanny = heartrate > 60
    update_display_and_sound(is_uncanny, dist)

    pg.display.flip()
    clock.tick(30)  # Set fps

pg.quit()
