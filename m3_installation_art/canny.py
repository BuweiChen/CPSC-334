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


def get_distance():
    return 0.0


def get_heartrate():
    return 0


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
