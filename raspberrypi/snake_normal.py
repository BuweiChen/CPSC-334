import curses
import random

# Initialize the curses screen
stdscr = curses.initscr()
curses.curs_set(0)  # Hide cursor
sh, sw = stdscr.getmaxyx()  # Screen height and width
w = curses.newwin(sh, sw, 0, 0)  # Create new window for the game
w.keypad(1)  # Enable keypad input for capturing arrow keys
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
    hard_mode = False  # This will be a GPIO toggle switch later

    while True:
        # Get the next input key from the user (for now, use keyboard arrows)
        next_key = w.getch()

        # Update direction based on key input (ignore if it's a 180-degree turn)
        if next_key != -1 and next_key != opposite_directions.get(direction):
            direction = next_key

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
    w.addstr(sh // 2 + 1, sw // 2 - 10, "Press any key to restart")
    w.refresh()

    # Wait for any key press to restart
    while w.getch() == -1:
        pass  # Wait until a key is pressed

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
        # Cleanup curses
        curses.endwin()
