import pygame
import random

# Initialize
pygame.init()

# Window settings
WIDTH, HEIGHT = 480, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishing")

# Font for score
font = pygame.font.SysFont(None, 24)

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Object sizes
BLACK_SIZE = 15     # Net
FISH_SIZE = 10      # Fish

# Net center position
BLACK_X = WIDTH // 2 - BLACK_SIZE // 2
BLACK_Y = HEIGHT // 2 - BLACK_SIZE // 2


def draw_fish(x, y, size=FISH_SIZE, color=GREEN):
    """Draw a scalable pixel fish with forked tail"""
    unit = size // 5
    pygame.draw.rect(screen, color, (x + unit, y, 2 * unit, unit))      # head
    pygame.draw.rect(screen, color, (x, y + unit, 4 * unit, 2 * unit))  # body
    pygame.draw.rect(screen, color, (x, y + 3 * unit, unit, unit))      # tail left
    pygame.draw.rect(screen, color, (x + 3 * unit, y + 3 * unit, unit, unit))  # tail right


def get_random_fish_position():
    """Get a random fish position far from the net and not in straight line directions"""
    margin = 100
    while True:
        x = random.randint(0, WIDTH - FISH_SIZE)
        y = random.randint(0, HEIGHT - FISH_SIZE)

        safe_left   = BLACK_X - margin - FISH_SIZE
        safe_right  = BLACK_X + BLACK_SIZE + margin
        safe_top    = BLACK_Y - margin - FISH_SIZE
        safe_bottom = BLACK_Y + BLACK_SIZE + margin

        if not (x + FISH_SIZE < safe_left or x > safe_right or y + FISH_SIZE < safe_top or y > safe_bottom):
            continue

        fish_center_x = x + FISH_SIZE // 2
        fish_center_y = y + FISH_SIZE // 2
        black_center_x = BLACK_X + BLACK_SIZE // 2
        black_center_y = BLACK_Y + BLACK_SIZE // 2

        if abs(fish_center_x - black_center_x) <= 2 or abs(fish_center_y - black_center_y) <= 2:
            continue

        return x, y


def get_required_directions(fx, fy):
    """Determine required key directions to catch the fish"""
    dirs = set()
    fish_center_x = fx + FISH_SIZE // 2
    fish_center_y = fy + FISH_SIZE // 2
    black_center_x = BLACK_X + BLACK_SIZE // 2
    black_center_y = BLACK_Y + BLACK_SIZE // 2
    if fish_center_x < black_center_x:
        dirs.add("left")
    elif fish_center_x > black_center_x:
        dirs.add("right")
    if fish_center_y < black_center_y:
        dirs.add("up")
    elif fish_center_y > black_center_y:
        dirs.add("down")
    return dirs


def draw_score(score):
    """Render score on screen"""
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))


def main():
    fish_x, fish_y = get_random_fish_position()
    required_directions = get_required_directions(fish_x, fish_y)
    pressed_directions = set()
    score = 0
    fish_caught = False
    last_spawn_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pressed_directions.add("left")
                elif event.key == pygame.K_RIGHT:
                    pressed_directions.add("right")
                elif event.key == pygame.K_UP:
                    pressed_directions.add("up")
                elif event.key == pygame.K_DOWN:
                    pressed_directions.add("down")

        if required_directions.issubset(pressed_directions):
            fish_caught = True

        if current_time - last_spawn_time > 5000 or fish_caught:
            if fish_caught:
                score += 1
            fish_x, fish_y = get_random_fish_position()
            required_directions = get_required_directions(fish_x, fish_y)
            pressed_directions.clear()
            fish_caught = False
            last_spawn_time = current_time

        # Draw scene
        screen.fill(BLUE)
        pygame.draw.rect(screen, BLACK, (BLACK_X, BLACK_Y, BLACK_SIZE, BLACK_SIZE))
        draw_fish(fish_x, fish_y, size=FISH_SIZE)
        draw_score(score)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
