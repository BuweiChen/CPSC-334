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
snake_speed = 5  # 10 frames per second

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

        # If the snake only has its head, it needs special handling when growing
        if len(self.body) == 1:
            self.body = [new_head]  # Update the head position
        else:
            self.body = [new_head] + self.body[:-1]  # Standard movement

        # Handle growth
        if self.growing:
            if len(self.body) == 1:
                # Special case: Snake only has a head, add a new tail piece in the same direction
                tail_x = head_x - self.direction[0] * block_size
                tail_y = head_y - self.direction[1] * block_size
                self.body.append((tail_x, tail_y))
            else:
                self.body.append(self.body[-1])  # Add a new segment to the tail
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
    def __init__(self, position, direction, screen_width, screen_height):
        self.start_position = position
        self.direction = direction
        self.positions = []
        self.alive = True
        self.fade_counter = 0  # Track fade duration (3 frames)
        self.deadly = True  # Deadly only for the initial frame

        # Determine the laser's path based on the direction
        if direction == (1, 0):  # Right
            self.positions = [
                (x, position[1])
                for x in range(position[0] + 2 * block_size, screen_width, block_size)
            ]
        elif direction == (-1, 0):  # Left
            self.positions = [
                (x, position[1])
                for x in range(position[0] - 2 * block_size, -1, -block_size)
            ]
        elif direction == (0, 1):  # Down
            self.positions = [
                (position[0], y)
                for y in range(position[1] + 2 * block_size, screen_height, block_size)
            ]
        elif direction == (0, -1):  # Up
            self.positions = [
                (position[0], y)
                for y in range(position[1] - 2 * block_size, -1, -block_size)
            ]

    def draw(self, surface):
        # Draw the laser as "#" for one frame
        for pos in self.positions:
            # pygame.draw.rect(
            #     surface, WHITE, pygame.Rect(pos[0], pos[1], block_size, block_size)
            # )
            surface.blit(font.render("#", True, WHITE), (pos[0], pos[1]))

    def fade(self, surface):
        # Draw the residual "*" effect (fade-out)
        if self.fade_counter < 3:
            for pos in self.positions:
                # pygame.draw.rect(
                #     surface, WHITE, pygame.Rect(pos[0], pos[1], block_size, block_size)
                # )
                if self.fade_counter == 0:
                    surface.blit(font.render("#", True, WHITE), (pos[0], pos[1]))
                else:
                    surface.blit(font.render("*", True, WHITE), (pos[0], pos[1]))
            self.fade_counter += 1
        else:
            self.alive = False  # Fade complete after 3 frames


def check_snake_collision(snake_1, snake_2):
    # Check if the head of snake_1 collides with any part of snake_2's body
    if snake_1.body[0] in snake_2.body:
        return True
    return False


def update_lasers(lasers, snake_1, snake_2):
    game_over = False
    for laser in lasers:
        if laser.deadly:
            # Check if the laser intersects with snake_1 or snake_2 only during the deadly phase
            for pos in laser.positions:
                if pos in snake_1.body[1:]:  # Hit snake_1's body
                    idx = snake_1.body.index(pos)
                    snake_1.body = snake_1.body[:idx]
                elif pos == snake_1.body[0]:  # Hit snake_1's head
                    game_over = True

                if pos in snake_2.body[1:]:  # Hit snake_2's body
                    idx = snake_2.body.index(pos)
                    snake_2.body = snake_2.body[:idx]
                elif pos == snake_2.body[0]:  # Hit snake_2's head
                    game_over = True

            laser.deadly = False  # After first frame, laser is no longer deadly

    return game_over


def handle_input(snake_1, snake_2, active_snake, lasers, screen_width, screen_height):
    global ser
    while ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()

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

                    # Fire laser when the button is pressed
                    if button_state == 0:
                        laser_direction = (
                            active_snake.direction
                        )  # Fire in the current direction
                        laser_position = active_snake.body[
                            0
                        ]  # Start at one block in front of the head of the snake
                        lasers.append(
                            Laser(
                                laser_position,
                                laser_direction,
                                screen_width,
                                screen_height,
                            )
                        )

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


def render_game(screen, snake_1, snake_2, apple, lasers, score, best_score):
    screen.fill(BLACK)
    snake_1.draw(screen)
    snake_2.draw(screen)
    apple.draw(screen)

    # Draw lasers
    for laser in lasers:
        if laser.deadly:  # Draw the deadly laser for 1 frame
            laser.draw(screen)
        elif laser.alive:  # Fade out the laser for 3 frames
            laser.fade(screen)

    # Render score and best score
    score_text = font.render(f"Score: {score}", True, WHITE)
    best_score_text = font.render(f"Best Score: {best_score}", True, WHITE)
    screen.blit(score_text, [10, 10])
    screen.blit(best_score_text, [screen_width - 150, 10])
    pygame.display.flip()

    # Remove lasers after the fade completes
    lasers[:] = [laser for laser in lasers if laser.alive]


def main():
    global best_score
    snake_1 = Snake(GREEN, 1)
    snake_2 = Snake(WHITE, 2)
    apple = Apple()
    active_snake = snake_1
    last_snake_to_eat = None
    score = 0
    lasers = []

    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Handle input and create lasers
        active_snake = handle_input(
            snake_1, snake_2, active_snake, lasers, screen_width, screen_height
        )

        # Update game state
        game_over, last_snake_to_eat = update_game(
            snake_1, snake_2, apple, active_snake, last_snake_to_eat
        )

        # Update lasers and check if they hit a snake
        if update_lasers(lasers, snake_1, snake_2):
            game_over = True  # If a laser hits a snake's head, game over

        # Render everything
        render_game(screen, snake_1, snake_2, apple, lasers, score, best_score)

        clock.tick(snake_speed)

    # Game Over: Add restart or quit functionality here
    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
