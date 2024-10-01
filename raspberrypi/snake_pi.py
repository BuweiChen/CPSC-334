import curses
import random
import RPi.GPIO as GPIO
import time

# GPIO setup
BUTTON_PIN = 16
JOYSTICK_X_PIN = 27
JOYSTICK_Y_PIN = 17
HARD_MODE_PIN = 21  # Toggle switch for hard mode

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYSTICK_X_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYSTICK_Y_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(HARD_MODE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the curses screen
stdscr = curses.initscr()
curses.curs_set(0)  # Hide cursor
sh, sw = stdscr.getmaxyx()  # Screen height and width
w = curses.newwin(sh, sw, 0, 0)  # Create new window for the game
w.timeout(100)  # Game speed, refresh every 100ms

# Snake starting position
snake_x = sw // 4
snake_y = sh // 2
snake = [[snake_y, snake_x], [snake_y, snake_x - 1], [snake_y, snake_x - 2]]

# Initial direction (right)
direction = curses.KEY_RIGHT

# Food setup
food = [sh // 2, sw // 2]
w.addch(int(food[0]), int(food[1]), curses.ACS_PI)

score = 0

# Opposite direction mapping to prevent 180-degree turn
opposite_directions = {
    curses.KEY_UP: curses.KEY_DOWN,
    curses.KEY_DOWN: curses.KEY_UP,
    curses.KEY_LEFT: curses.KEY_RIGHT,
    curses.KEY_RIGHT: curses.KEY_LEFT,
}


# Game loop
def main():
    global direction, score, food, snake
    hard_mode = False  # This will be controlled by the toggle switch later

    while True:
        # Check if the hard mode switch is flipped
        if GPIO.input(HARD_MODE_PIN) == GPIO.LOW:
            hard_mode = not hard_mode
            time.sleep(0.5)  # Debounce switch

        # Poll for button press and read joystick direction
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

        # Move snake based on the current direction
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

        # Check if snake eats food
        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [random.randint(1, sh - 1), random.randint(1, sw - 1)]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(int(tail[0]), int(tail[1]), " ")

        # Game over conditions (wall or self-collision)
        if snake[0][0] in [0, sh] or snake[0][1] in [0, sw] or snake[0] in snake[1:]:
            game_over()

        # Draw snake
        w.addch(int(snake[0][0]), int(snake[0][1]), curses.ACS_CKBOARD)

        # Display score
        w.addstr(0, 2, "Score: " + str(score))


def game_over():
    # Display game over message
    w.clear()
    w.addstr(sh // 2, sw // 2 - 7, "GAME OVER")
    w.addstr(sh // 2 + 1, sw // 2 - 10, "Press button to restart")
    w.refresh()

    # Wait for button press to restart
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        pass  # Wait until button is pressed

    restart_game()


def restart_game():
    global snake, direction, score, food

    # Clear the screen for the new game
    w.clear()

    # Reset snake, direction, and score
    snake_x = sw // 4
    snake_y = sh // 2
    snake = [[snake_y, snake_x], [snake_y, snake_x - 1], [snake_y, snake_x - 2]]
    direction = curses.KEY_RIGHT
    score = 0

    # Reset food position
    food = [sh // 2, sw // 2]
    w.addch(int(food[0]), int(food[1]), curses.ACS_PI)

    # Refresh screen for new game state
    w.refresh()


if __name__ == "__main__":
    try:
        main()
    finally:
        # Cleanup GPIO and curses
        GPIO.cleanup()
        curses.endwin()
