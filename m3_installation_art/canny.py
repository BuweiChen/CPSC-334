import pygame as pg

import os

import socket

import threading

pg.init()

# screen setting
screen = pg.display.set_mode((800, 600))

# pwd
dir_path = os.path.dirname(os.path.realpath(__file__))

# Global variables to store distance and heart rate
current_distance = 0.0
current_heartrate = 0

# ESP32 server settings
ESP32_IP = "10.67.68.95"
ESP32_PORT = 80

def get_distance():
    return current_distance


def get_heartrate():
    return current_heartrate

def update_sensor_data():
    global current_distance, current_heartrate
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ESP32_IP, ESP32_PORT))

            while True:
                data = sock.recv(1024).decode("utf-8").strip()
                if not data:
                    continue

                for line in data.splitlines():
                    # Parse data lines
                    if "Heart Rate (BPM):" in line:
                        current_heartrate = int(line.split(":")[1].strip())
                    elif "Distance (cm):" in line:
                        current_distance = float(line.split(":")[1].strip())
                    else:
                        # Handle empty lines or unrecognized data
                        continue
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        print(f"Connection error: {e}")


def display_image(image_path):
    image = pg.image.load(image_path)
    image = pg.transform.scale(image, (800, 600))
    screen.blit(image, (0, 0))


def play_music(music_path):
    pg.mixer.music.load(music_path)
    pg.mixer.music.play(-1, 0.0)


def get_full_filepath(path):
    return os.path.join(dir_path, "media", path)


clock = pg.time.Clock()
start_time = pg.time.get_ticks()

done = False
curr_sound_playing = None

# Run the client in a background thread to constantly update data
sensor_thread = threading.Thread(target=update_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

    if get_heartrate() > 60:
        dist = get_distance()
        if dist < 30:
            display_image(get_full_filepath("uncanny5.png"))
            if curr_sound_playing != "uncanny5.mp3":
                play_music(get_full_filepath("uncanny5.mp3"))
                curr_sound_playing = "uncanny5.mp3"
        if dist < 60:
            display_image(get_full_filepath("uncanny4.png"))
            if curr_sound_playing != "uncanny4.mp3":
                play_music(get_full_filepath("uncanny4.mp3"))
                curr_sound_playing = "uncanny4.mp3"
        if dist < 90:
            display_image(get_full_filepath("uncanny3.png"))
            if curr_sound_playing != "uncanny3.mp3":
                play_music(get_full_filepath("uncanny3.mp3"))
                curr_sound_playing = "uncanny3.mp3"
        if dist < 120:
            display_image(get_full_filepath("uncanny2.png"))
            if curr_sound_playing != "uncanny2.mp3":
                play_music(get_full_filepath("uncanny2.mp3"))
                curr_sound_playing = "uncanny2.mp3"

        display_image(get_full_filepath("uncanny1.png"))
        if curr_sound_playing != "uncanny1.mp3":
            play_music(get_full_filepath("uncanny1.mp3"))
            curr_sound_playing = "uncanny1.mp3"
    else:
        if dist < 30:
            display_image(get_full_filepath("canny5.png"))
            if curr_sound_playing != "canny5.mp3":
                play_music(get_full_filepath("canny5.mp3"))
                curr_sound_playing = "canny5.mp3"
        if dist < 60:
            display_image(get_full_filepath("canny4.png"))
            if curr_sound_playing != "canny4.mp3":
                play_music(get_full_filepath("canny4.mp3"))
                curr_sound_playing = "canny4.mp3"
        if dist < 90:
            display_image(get_full_filepath("canny3.png"))
            if curr_sound_playing != "canny3.mp3":
                play_music(get_full_filepath("canny3.mp3"))
                curr_sound_playing = "canny3.mp3"
        if dist < 120:
            display_image(get_full_filepath("canny2.png"))
            if curr_sound_playing != "canny2.mp3":
                play_music(get_full_filepath("canny2.mp3"))
                curr_sound_playing = "canny2.mp3"

        display_image(get_full_filepath("canny1.png"))
        if curr_sound_playing != "canny1.mp3":
            play_music(get_full_filepath("canny1.mp3"))
            curr_sound_playing = "canny1.mp3"

    pg.display.flip()
    clock.tick(20)  # Set fps
