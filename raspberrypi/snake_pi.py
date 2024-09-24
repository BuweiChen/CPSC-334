from random import randint
import RPi.GPIO as GPIO
import time
import curses

BUTTON_PIN = 16
JOYSTICK_X_PIN = 27
JOYSTICK_Y_PIN = 17
HARD_MODE_PIN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYSTICK_X_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYSTICK_Y_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(HARD_MODE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

stdscr = curses.initscr()
curses.curs_set(0)
sh, sw = stdscr.getmaxyx()
w = curses.newwin(sh, sw, 0, 0)
w.timeout(100)  # Snake speed (refresh rate in ms)

snake_x = sw // 4
snake_y = sh // 2
snake = [[snake_y, snake_x], [snake_y, snake_x - 1], [snake_y, snake_x - 2]]

direction = curses.KEY_RIGHT

food = [sh // 2, sw // 2]
w.addch(int(food[0]), int(food[1]), curses.ACS_PI)

score = 0

opposite_directions = {
    curses.KEY_UP: curses.KEY_DOWN,
    curses.KEY_DOWN: curses.KEY_UP,
    curses.KEY_LEFT: curses.KEY_RIGHT,
    curses.KEY_RIGHT: curses.KEY_LEFT,
}


def main():
    global direction, score
    hard_mode = False

    while True:
        if GPIO.input(HARD_MODE_PIN) == GPIO.LOW:
            hard_mode = not hard_mode
            time.sleep(0.5)  # Debounce switch

        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.2)  # Debounce button
            joy_x = GPIO.input(JOYSTICK_X_PIN)
            joy_y = GPIO.input(JOYSTICK_Y_PIN)

            # Determine the new direction based on joystick input
            new_direction = direction  # Keep the current direction as default
            if joy_x == GPIO.LOW:
                new_direction = curses.KEY_LEFT if not hard_mode else curses.KEY_RIGHT
            elif joy_x == GPIO.HIGH:
                new_direction = curses.KEY_RIGHT if not hard_mode else curses.KEY_LEFT
            if joy_y == GPIO.LOW:
                new_direction = curses.KEY_UP if not hard_mode else curses.KEY_DOWN
            elif joy_y == GPIO.HIGH:
                new_direction = curses.KEY_DOWN if not hard_mode else curses.KEY_UP

            # Only update the direction if it's not the opposite of the current direction
            if new_direction != opposite_directions.get(direction):
                direction = new_direction

        head = snake[0]
        if direction == curses.KEY_RIGHT:
            new_head = [head[0], head[1] + 1]
        elif direction == curses.KEY_LEFT:
            new_head = [head[0], head[1] - 1]
        elif direction == curses.KEY_UP:
            new_head = [head[0] - 1, head[1]]
        elif direction == curses.KEY_DOWN:
            new_head = [head[0] + 1, head[1]]

        snake.insert(0, new_head)

        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [randint(1, sh - 1), randint(1, sw - 1)]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(int(tail[0]), int(tail[1]), " ")

        if snake[0][0] in [0, sh] or snake[0][1] in [0, sw] or snake[0] in snake[1:]:
            w.clear()
            w.addstr(sh // 2, sw // 2 - 7, "GAME OVER")
            w.addstr(sh // 2 + 1, sw // 2 - 10, "Press Button to Restart")
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                pass
            restart_game()

        w.addch(int(snake[0][0]), int(snake[0][1]), curses.ACS_CKBOARD)

        w.addstr(0, 2, "Score: " + str(score))


def restart_game():
    global snake, direction, score, food
    snake_x = sw // 4
    snake_y = sh // 2
    snake = [[snake_y, snake_x], [snake_y, snake_x - 1], [snake_y, snake_x - 2]]
    direction = curses.KEY_RIGHT
    score = 0
    food = [sh // 2, sw // 2]
    w.addch(int(food[0]), int(food[1]), curses.ACS_PI)


if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()
        curses.endwin()
