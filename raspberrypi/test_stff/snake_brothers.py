import pygame
import random
import serial

# Initialize pygame and set up the display
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Two Snake Game")

# Set up font for score display
font = pygame.font.Font(None, 36)

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set the speed and block size
block_size = 20

# Initialize joystick
ser = serial.Serial("/dev/tty.usbserial-1130", 115200, timeout=1)
ser.flush()

# Clock to control the frame rate
clock = pygame.time.Clock()

# Global variables for score tracking
best_score = 0

# fps
clock = pygame.time.Clock()
snake_speed = 10  # 10 frames per second

last_snake_to_eat = None


class Snake:
    def __init__(self, color, id):
        if id == 1:
            self.body = [(100, 40), (80, 40), (60, 40)]  # Starting position
            self.direction = (1, 0)  # Starts moving to the right
        else:
            self.body = [
                (screen_width - 100, 40),
                (screen_width - 80, 40),
                (screen_width - 60, 40),
            ]  # Starting position
            self.direction = (-1, 0)  # Starts moving to the left
        self.growing = False
        self.color = color

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (
            head_x + self.direction[0] * block_size,
            head_y + self.direction[1] * block_size,
        )
        self.body = [new_head] + self.body[:-1]
        if self.growing:
            self.body.append(self.body[-1])
            self.growing = False

    def grow(self):
        self.growing = True

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(
                surface,
                self.color,
                pygame.Rect(segment[0], segment[1], block_size, block_size),
            )

    def collided_with_self(self):
        head = self.body[0]
        return head in self.body[1:]

    def collided_with_wall(self, width, height):
        head_x, head_y = self.body[0]
        return not (0 <= head_x < width and 0 <= head_y < height)


class Apple:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        return (
            random.randint(0, (screen_width // block_size) - 1) * block_size,
            random.randint(0, (screen_height // block_size) - 1) * block_size,
        )

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            RED,
            pygame.Rect(self.position[0], self.position[1], block_size, block_size),
        )


class Laser:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.alive = True  # Laser exists only for one frame

    def move(self):
        # Update laser position based on direction
        self.position = (
            self.position[0] + self.direction[0] * block_size,
            self.position[1] + self.direction[1] * block_size,
        )

    def draw(self, surface):
        # Draw laser as "#"
        pygame.draw.rect(
            surface,
            WHITE,
            pygame.Rect(self.position[0], self.position[1], block_size, block_size),
        )
        surface.blit(
            font.render("#", True, WHITE), (self.position[0], self.position[1])
        )

    def fade(self, surface):
        # Draw the residual "*" effect (fade-out)
        pygame.draw.rect(
            surface,
            WHITE,
            pygame.Rect(self.position[0], self.position[1], block_size, block_size),
        )
        surface.blit(
            font.render("*", True, WHITE), (self.position[0], self.position[1])
        )


def check_snake_collision(snake_1, snake_2):
    # Check if the head of snake_1 collides with any part of snake_2's body
    if snake_1.body[0] in snake_2.body:
        return True
    return False


def handle_input(snake_1, snake_2, active_snake):
    global ser
    while ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()

        # Check if the line is not empty
        if line:
            data = line.split(",")
            if len(data) == 4:  # Ensure we have exactly 4 values
                try:
                    x_value, y_value, button_state, switch_state = map(int, data)

                    # Define the neutral region
                    neutral = 457
                    neutral_tolerance = 10
                    max_deviation = 1023 - neutral

                    # Calculate deviation percentages for x and y
                    x_deviation = abs(x_value - neutral) / max_deviation
                    y_deviation = abs(y_value - neutral) / max_deviation

                    # If the joystick is outside the neutral zone, choose the direction with greater deviation
                    if (
                        max(x_deviation, y_deviation)
                        > neutral_tolerance / max_deviation
                    ):
                        if x_deviation > y_deviation:  # x-axis movement
                            if (
                                x_value > neutral + neutral_tolerance
                                and active_snake.direction != (-1, 0)
                            ):
                                active_snake.direction = (1, 0)  # Move right
                            elif (
                                x_value < neutral - neutral_tolerance
                                and active_snake.direction != (1, 0)
                            ):
                                active_snake.direction = (-1, 0)  # Move left
                        else:  # y-axis movement
                            if (
                                y_value > neutral + neutral_tolerance
                                and active_snake.direction != (0, -1)
                            ):
                                active_snake.direction = (0, 1)  # Move down
                            elif (
                                y_value < neutral - neutral_tolerance
                                and active_snake.direction != (0, 1)
                            ):
                                active_snake.direction = (0, -1)  # Move up

                    # Handle switching between snakes
                    if switch_state == 1:
                        active_snake = snake_2
                    else:
                        active_snake = snake_1

                except ValueError:
                    pass  # Ignore malformed data silently

    return active_snake


def update_game(snake_1, snake_2, apple, active_snake, last_snake_to_eat):
    # Move only the active snake
    active_snake.move()

    # Check if the active snake has eaten the apple and if it's its turn
    if active_snake.body[0] == apple.position:
        if active_snake != last_snake_to_eat:
            active_snake.grow()
            apple.position = apple.random_position()
            last_snake_to_eat = active_snake

    # Check for self-collision and wall collision for the active snake
    if active_snake.collided_with_self() or active_snake.collided_with_wall(
        screen_width, screen_height
    ):
        return True, last_snake_to_eat  # Game over

    # Check if the active snake collides with the other snake
    other_snake = snake_2 if active_snake == snake_1 else snake_1
    if check_snake_collision(active_snake, other_snake):
        return True, last_snake_to_eat  # Game over if collision between snakes

    return False, last_snake_to_eat  # Game continues


def render_game(screen, snake_1, snake_2, apple, score, best_score):
    screen.fill(BLACK)
    snake_1.draw(screen)
    snake_2.draw(screen)
    apple.draw(screen)

    # Render score and best score
    score_text = font.render(f"Score: {score}", True, WHITE)
    best_score_text = font.render(f"Best Score: {best_score}", True, WHITE)
    screen.blit(score_text, [10, 10])
    screen.blit(best_score_text, [screen_width - 200, 10])
    pygame.display.flip()


def main():
    global best_score, last_snake_to_eat
    snake_1 = Snake(GREEN, 1)
    snake_2 = Snake(WHITE, 2)
    apple = Apple()
    active_snake = snake_1
    last_snake_to_eat = None
    score = 0

    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Handle input
        active_snake = handle_input(snake_1, snake_2, active_snake)

        # Update game state
        game_over, last_snake_to_eat = update_game(
            snake_1, snake_2, apple, active_snake, last_snake_to_eat
        )

        # Render everything
        render_game(screen, snake_1, snake_2, apple, score, best_score)

        clock.tick(snake_speed)

    # Game Over: Add restart or quit functionality here
    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
