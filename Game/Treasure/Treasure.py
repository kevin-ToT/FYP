import os
import pygame
import random

# Initialize
pygame.init()

# Window settings
WIDTH, HEIGHT = 480, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Hunt")

# Font for score
font = pygame.font.SysFont(None, 24)

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)

# Sizes
PLAYER_SIZE = 10  # Black block (player)
TREASURE_SIZE = 30  # Treasure

base_path = os.path.dirname(os.path.abspath(__file__))
treasure_path = os.path.join(base_path, "treasure.png")

# Movement speed
STEP = 10

# Initial player position (center)
player_x = WIDTH // 2 - PLAYER_SIZE // 2
player_y = HEIGHT // 2 - PLAYER_SIZE // 2

def draw_treasure(x, y):
    screen.blit(treasure_img, (x, y))

def get_random_treasure_position():
    """Generate random position for treasure"""
    x = random.randint(0, WIDTH - TREASURE_SIZE)
    y = random.randint(0, HEIGHT - TREASURE_SIZE)
    return x, y


def draw_score(score):
    """Render score on screen"""
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

treasure_img = pygame.image.load(treasure_path).convert_alpha()
treasure_img = pygame.transform.smoothscale(treasure_img, (TREASURE_SIZE, TREASURE_SIZE))

def main():
    global player_x, player_y
    treasure_x, treasure_y = get_random_treasure_position()
    score = 0

    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(30)  # Limit FPS to 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movement keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= STEP
        if keys[pygame.K_RIGHT]:
            player_x += STEP
        if keys[pygame.K_UP]:
            player_y -= STEP
        if keys[pygame.K_DOWN]:
            player_y += STEP

        # Keep player within bounds
        player_x = max(0, min(WIDTH - PLAYER_SIZE, player_x))
        player_y = max(0, min(HEIGHT - PLAYER_SIZE, player_y))

        # Check collision (edge touching counts)
        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
        treasure_rect = pygame.Rect(treasure_x, treasure_y, TREASURE_SIZE, TREASURE_SIZE)
        if player_rect.colliderect(treasure_rect):
            score += 1
            treasure_x, treasure_y = get_random_treasure_position()

        # Draw everything
        screen.fill(BLUE)
        pygame.draw.rect(screen, BLACK, player_rect)  # Player
        draw_treasure(treasure_x, treasure_y)
        draw_score(score)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
