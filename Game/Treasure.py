import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# Game UI
WIDTH = 1280
HEIGHT = 720
GRID_SIZE = 20
FPS = 10

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 初始化屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇游戏")

clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = [(WIDTH//2, HEIGHT//2)]
        self.direction = (0, 0)
        self.score = 0
    
    def move(self):
        if self.direction == (0, 0):
            return
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0] * GRID_SIZE,
                    head_y + self.direction[1] * GRID_SIZE)
        self.body.insert(0, new_head)
        self.body.pop()
    
    def grow(self):
        self.body.append(self.body[-1])
        self.score += 10
    
    def check_collision(self):
        head = self.body[0]
        # 边界检测
        if (head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT):
            return True
        # 自碰检测
        if head in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        x = random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        self.position = (x, y)

def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def game_loop():
    snake = Snake()
    food = Food()
    
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
        
        # 游戏逻辑
        snake.move()
        
        # 食物碰撞检测
        if snake.body[0] == food.position:
            snake.grow()
            food.randomize_position()
        
        # 碰撞检测
        if snake.check_collision():
            return
        
        # 绘制界面
        screen.fill(BLACK)
        
        # 绘制蛇
        for idx, segment in enumerate(snake.body):
            color = GREEN if idx == 0 else BLUE
            pygame.draw.rect(screen, color, (segment[0], segment[1], GRID_SIZE-1, GRID_SIZE-1))
        
        # 绘制食物
        pygame.draw.rect(screen, RED, (food.position[0], food.position[1], GRID_SIZE-1, GRID_SIZE-1))
        
        # 显示分数
        draw_text(f"Score: {snake.score}", 30, WHITE, WIDTH//2, 20)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_over():
    while True:
        screen.fill(BLACK)
        draw_text("Game Over!", 50, RED, WIDTH//2, HEIGHT//2 - 40)
        draw_text("Press R to restart, Q to quit", 30, WHITE, WIDTH//2, HEIGHT//2 + 20)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# 主游戏循环
while True:
    game_loop()
    game_over()