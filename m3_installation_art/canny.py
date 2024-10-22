import pygame as pg

import os

pg.init()

# screen setting
screen = pg.display.set_mode((800, 600))

# pwd
dir_path = os.path.dirname(os.path.realpath(__file__))

media_files = {
    "uncanny": {
        "1": {
            "image": "uncanny1.png",
            "music": "uncanny1.mp3",
        },
        "2": {
            "image": "uncanny2.png",
            "music": "uncanny2.mp3",
        },
        "3": {
            "image": "uncanny3.png",
            "music": "uncanny3.mp3",
        },
        "4": {
            "image": "uncanny4.png",
            "music": "uncanny4.mp3",
        },
        "5": {
            "image": "uncanny5.png",
            "music": "uncanny5.mp3",
        },
    },
    "canny": {
        "1": {
            "image": "canny1.png",
            "music": "canny1.mp3",
        },
        "2": {
            "image": "canny2.png",
            "music": "canny2.mp3",
        },
        "3": {
            "image": "canny3.png",
            "music": "canny3.mp3",
        },
        "4": {
            "image": "canny4.png",
            "music": "canny4.mp3",
        },
        "5": {
            "image": "canny5.png",
            "music": "canny5.mp3",
        },
    },
}


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
click_time = 0
passed_time = 0

done = False
curr_sound_playing = None

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        # Start the timer.
        elif event.type == pg.MOUSEBUTTONDOWN:
            click_time = pg.time.get_ticks()

    screen.fill((30, 30, 30))
    if click_time != 0:  # If timer has been started.
        # Calculate the passed time since the click.
        passed_time = (pg.time.get_ticks() - click_time) / 1000

    # If 3 seconds have passed, blit the image.
    if passed_time >= 3:
        display_image(get_full_filepath("uncanny1.png"))
        if curr_sound_playing != "uncanny1.mp3":
            play_music(get_full_filepath("uncanny1.mp3"))
            curr_sound_playing = "uncanny1.mp3"
    else:
        display_image(get_full_filepath("uncanny2.png"))
        if curr_sound_playing != "uncanny2.mp3":
            play_music(get_full_filepath("uncanny2.mp3"))
            curr_sound_playing = "uncanny2.mp3"

    pg.display.flip()
    clock.tick(20)  # Set fps
