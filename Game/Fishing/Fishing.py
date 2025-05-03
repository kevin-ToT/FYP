import pygame
import random
import os
import sys

from controller import DynamixelController

ini_motor_params = {
    'left': {'motor_id': 1, 'movement': 0},
    'right': {'motor_id': 1, 'movement': 0},
}

motor_params = {
    'left': {'motor_id': 1, 'movement': -367},
    'right': {'motor_id': 1, 'movement': 367},
    'up': {'motor_id': 2, 'movement': 367},
    'down': {'motor_id': 2, 'movement': -367},
}

def map_value(value, from_min, from_max, to_min, to_max):
    return to_min + (float(value - from_min) / (from_max - from_min)) * (to_max - to_min)

# Initialize
pygame.init()
# Initialize Dynamixel controller
controller = DynamixelController()
if not controller.initialize():
    print("Dynamixel controller initialization failed.")
    sys.exit(1)
# Initial position commands
controller.move_to_position(1, [0])
controller.move_to_position(2, [0])

# Window settings
WIDTH, HEIGHT = 480, 360
SEA_HEIGHT = 280
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishing From Shore")

# Font
font = pygame.font.SysFont("arial", 22)

# Colors
BLUE = (0, 0, 255)
GREEN = (0, 155, 0)
WHITE = (255, 255, 255)

# Sizes
PLAYER_SIZE = 50
FISH_SIZE = 30

# Struggle settings
HORIZON_STRUGGLES = 3    # horizontal struggles before vertical
MAX_STRUGGLES = 10       # total struggles per catch

# Opposite map for horizontal
opp_map = {'left': 'right', 'right': 'left'}

# Load images
def load_image(filename, size):
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        sys.exit(1)

fish_img = load_image("fish.png", (FISH_SIZE, FISH_SIZE))
player_img = load_image("player.png", (PLAYER_SIZE, PLAYER_SIZE))

# Player (shore) position
PLAYER_X = WIDTH // 2 - PLAYER_SIZE // 2
PLAYER_Y = SEA_HEIGHT - 10

# Utilities
def get_random_fish_position():
    return (random.randint(0, WIDTH - FISH_SIZE), random.randint(0, SEA_HEIGHT - FISH_SIZE - 30))

# Draw functions
def draw_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def draw_ground_text(msg):
    text = font.render(msg, True, WHITE)
    rect = text.get_rect(center=(WIDTH // 2, SEA_HEIGHT + 60))
    screen.blit(text, rect)

# Main game loop
def run_game():
    global motor_params

    fish_x, fish_y = get_random_fish_position()
    score = 0
    state = "waiting_start"
    initial_dir = None
    initial_moved = False  # flag for controller move
    struggle_done = 0
    horiz_count = 0
    instruction = None

    clock = pygame.time.Clock()
    running = True

    def generate_struggle():
        nonlocal fish_x, fish_y, instruction, horiz_count
        prev_x, prev_y = fish_x, fish_y

        # Horizontal phase
        if horiz_count < HORIZON_STRUGGLES:
            fish_y = prev_y
            fish_x, _ = get_random_fish_position()
            instruction = 'left' if fish_x < prev_x else 'right'
            horiz_count += 1
        else:
            # Vertical phase
            instruction = random.choice(['up', 'down'])
            dy = random.randint(10, SEA_HEIGHT // 4)
            fish_x = prev_x
            fish_y = max(0, prev_y - dy) if instruction == 'up' else min(SEA_HEIGHT - FISH_SIZE - 30, prev_y + dy)
            horiz_count = 0

        # 立即显示鱼的位置变化
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SEA_HEIGHT, WIDTH, HEIGHT - SEA_HEIGHT))
        screen.blit(fish_img, (fish_x, fish_y))
        screen.blit(player_img, (PLAYER_X, PLAYER_Y))
        draw_score(score)
        pygame.display.flip()

        # 先等待2秒
        pygame.time.delay(1500)

        # 再执行控制器动作提示
        param = motor_params[instruction]
        controller.move_to_position(param['motor_id'], [param['movement'], 0])

    # Arrow icons for display
    arrow_map = {'left': '<-', 'right': '->', 'up': '^', 'down': 'v'}

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == 'waiting_start' and event.key == pygame.K_SPACE:
                    initial_dir = 'left' if fish_x < PLAYER_X else 'right'

                    if initial_dir == 'left':
                        mapped_movement = int(map_value(fish_x, 0, PLAYER_X, -600, -100))
                        ini_motor_params['left']['movement'] = mapped_movement
                    else:
                        mapped_movement = int(map_value(fish_x, PLAYER_X, WIDTH - FISH_SIZE, 100, 600))
                        ini_motor_params['right']['movement'] = mapped_movement

                    state = 'direction_judgment'
                    initial_moved = False
                elif state == 'direction_judgment':
                    if ((event.key == pygame.K_LEFT and initial_dir == 'left') or
                        (event.key == pygame.K_RIGHT and initial_dir == 'right')):
                        struggle_done = horiz_count = 0

                        motor_params = {
                            'left': motor_params['left'].copy(),
                            'right': motor_params['right'].copy(),
                            'up': motor_params['up'].copy(),
                            'down': motor_params['down'].copy(),
                        }

                        generate_struggle()
                        state = 'struggle_phase'
                        initial_moved = False
                    else:
                        state = 'waiting_start'
                elif state == 'struggle_phase':
                    key_map = {pygame.K_LEFT: 'left', pygame.K_RIGHT: 'right', pygame.K_UP: 'up', pygame.K_DOWN: 'down'}
                    key_dir = key_map.get(event.key)
                    if instruction in ['left', 'right']:
                        correct = (key_dir == opp_map[instruction])
                    else:
                        correct = (key_dir == instruction)
                    if correct:
                        struggle_done += 1
                        if struggle_done >= MAX_STRUGGLES:
                            score += 1
                            fish_x, fish_y = get_random_fish_position()
                            state = 'waiting_start'
                        else:
                            generate_struggle()
                    else:
                        state = 'waiting_start'

        # Drawing
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SEA_HEIGHT, WIDTH, HEIGHT - SEA_HEIGHT))
        screen.blit(fish_img, (fish_x, fish_y))
        screen.blit(player_img, (PLAYER_X, PLAYER_Y))
        draw_score(score)

        if state == 'waiting_start':
            draw_ground_text('Press SPACE to start')
        elif state == 'direction_judgment':
            draw_ground_text(f'Fish at {initial_dir.capitalize()}! Press {arrow_map[initial_dir]} to fish')
            pygame.display.flip()
            if not initial_moved:
                param = ini_motor_params[initial_dir]
                controller.move_to_position(param['motor_id'], [param['movement'], 0])
                pygame.time.delay(1000)
                initial_moved = True
            continue
        elif state == 'struggle_phase':
            dir_word = instruction.capitalize()
            expected = arrow_map[opp_map[instruction]] if instruction in ['left','right'] else arrow_map[instruction]
            # draw_ground_text(f'Fish jumps {dir_word}! Press {expected}')

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    try:
        run_game()
    finally:
        controller.close()

