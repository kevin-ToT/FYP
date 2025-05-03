import os
import pygame
import random
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 480, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Treasure Hunt")

# Font for score
game_font = pygame.font.SysFont(None, 24)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 128)
GOLD = (255, 215, 0)

# Maze settings
CELL_SIZE = 35
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

# Player settings
PLAYER_SIZE = 10  # in pixels
player_cell_x = random.randrange(COLS)
player_cell_y = random.randrange(ROWS)

# Treasure settings
TREASURE_SIZE = 16  # in pixels

# Maximum allowed steps (最优路径上限)
MAX_STEPS = 20

def generate_maze(cols, rows):
    # walls[y][x] = [top, right, bottom, left]
    walls = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def neighbors(cx, cy):
        nbrs = []
        if cy > 0 and not visited[cy - 1][cx]:
            nbrs.append((cx, cy - 1, 0, 2))
        if cx < cols - 1 and not visited[cy][cx + 1]:
            nbrs.append((cx + 1, cy, 1, 3))
        if cy < rows - 1 and not visited[cy + 1][cx]:
            nbrs.append((cx, cy + 1, 2, 0))
        if cx > 0 and not visited[cy][cx - 1]:
            nbrs.append((cx - 1, cy, 3, 1))
        return nbrs

    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        cx, cy = stack[-1]
        nbrs = neighbors(cx, cy)
        if nbrs:
            nx, ny, w, ow = random.choice(nbrs)
            walls[cy][cx][w] = False
            walls[ny][nx][ow] = False
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()

    return walls

def carve_extra_paths(walls, extra=0.1):
    """
    在 walls 上随机移除额外墙壁，制造环路。 
    extra: 要打通的格子比例（如 0.1 即尝试打通 10% 的格子）。
    """
    total_cells = COLS * ROWS
    attempts = int(total_cells * extra)
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    for _ in range(attempts):
        x = random.randrange(COLS)
        y = random.randrange(ROWS)
        dir_idx = random.randrange(4)
        if walls[y][x][dir_idx]:
            nx, ny = x + dirs[dir_idx][0], y + dirs[dir_idx][1]
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                opp = (dir_idx + 2) % 4
                walls[y][x][dir_idx] = False
                walls[ny][nx][opp] = False

def compute_distances(sx, sy, walls):
    """
    从 (sx,sy) 做 BFS，返回 dist[y][x] = 最短步数或 None。
    """
    dist = [[None]*COLS for _ in range(ROWS)]
    q = deque([(sx, sy)])
    dist[sy][sx] = 0
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    while q:
        x, y = q.popleft()
        for dir_idx, (dx, dy) in enumerate(dirs):
            if not walls[y][x][dir_idx]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and dist[ny][nx] is None:
                    dist[ny][nx] = dist[y][x] + 1
                    q.append((nx, ny))
    return dist

def random_treasure_cell():
    dist = compute_distances(player_cell_x, player_cell_y, walls)
    choices = [
        (x, y)
        for x in range(COLS) for y in range(ROWS)
        if dist[y][x] is not None
           and dist[y][x] <= MAX_STEPS
           and not (x == player_cell_x and y == player_cell_y)
    ]
    if not choices:
        # 若无格子满足 ≤MAX_STEPS，则退回到任何可达格子
        choices = [
            (x, y)
            for x in range(COLS) for y in range(ROWS)
            if dist[y][x] is not None
               and not (x == player_cell_x and y == player_cell_y)
        ]
    return random.choice(choices)

# 生成并修改迷宫
walls = generate_maze(COLS, ROWS)
carve_extra_paths(walls, extra=0.6)

# 放置宝藏
treasure_cell_x, treasure_cell_y = random_treasure_cell()

# Draw functions
def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            px, py = x * CELL_SIZE, y * CELL_SIZE
            top, right, bottom, left = walls[y][x]
            if top:
                pygame.draw.line(screen, WHITE, (px, py), (px + CELL_SIZE, py))
            if right:
                pygame.draw.line(screen, WHITE, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE))
            if bottom:
                pygame.draw.line(screen, WHITE, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE))
            if left:
                pygame.draw.line(screen, WHITE, (px, py), (px, py + CELL_SIZE))

def draw_player(x, y):
    px = x * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2
    py = y * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2
    pygame.draw.rect(screen, BLUE, (px, py, PLAYER_SIZE, PLAYER_SIZE))

def draw_treasure(x, y):
    tx = x * CELL_SIZE + (CELL_SIZE - TREASURE_SIZE) // 2
    ty = y * CELL_SIZE + (CELL_SIZE - TREASURE_SIZE) // 2
    pygame.draw.circle(screen, GOLD, (tx + TREASURE_SIZE // 2, ty + TREASURE_SIZE // 2), TREASURE_SIZE // 2)

def draw_score(score):
    txt = game_font.render(f"Score: {score}", True, WHITE)
    screen.blit(txt, (10, 10))

# Main game loop
def main():
    global player_cell_x, player_cell_y, treasure_cell_x, treasure_cell_y
    score = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not walls[player_cell_y][player_cell_x][3]:
                    player_cell_x -= 1
                elif event.key == pygame.K_RIGHT and not walls[player_cell_y][player_cell_x][1]:
                    player_cell_x += 1
                elif event.key == pygame.K_UP and not walls[player_cell_y][player_cell_x][0]:
                    player_cell_y -= 1
                elif event.key == pygame.K_DOWN and not walls[player_cell_y][player_cell_x][2]:
                    player_cell_y += 1

        # Check if player found treasure
        if (player_cell_x, player_cell_y) == (treasure_cell_x, treasure_cell_y):
            score += 1
            treasure_cell_x, treasure_cell_y = random_treasure_cell()

        # Draw everything
        screen.fill((0, 0, 0))
        draw_maze()
        draw_player(player_cell_x, player_cell_y)
        draw_treasure(treasure_cell_x, treasure_cell_y)
        draw_score(score)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
