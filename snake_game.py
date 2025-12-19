import pygame
import random
import sys
from typing import List, Tuple

# -----------------------------
# Config
# -----------------------------
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
CELL_SIZE = 20  # grid size
FPS = 5  # game speed

# Derived
GRID_COLS = WINDOW_WIDTH // CELL_SIZE
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 0, 0)
DARK_GRAY = (40, 40, 40)
BLUE = (0, 120, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self, start_pos: Tuple[int, int]):
        # snake body stored as list of grid positions (col, row)
        self.body: List[Tuple[int, int]] = [start_pos, (start_pos[0] - 1, start_pos[1]), (start_pos[0] - 2, start_pos[1])]
        self.direction: Tuple[int, int] = RIGHT
        self.grow_pending = 0

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reversing directly into itself
        if (self.direction[0] + new_dir[0] == 0) and (self.direction[1] + new_dir[1] == 0):
            return
        self.direction = new_dir

    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()  # remove tail

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def hits_wall(self) -> bool:
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_COLS and 0 <= head_y < GRID_ROWS)

    def hits_self(self) -> bool:
        return self.body[0] in self.body[1:]


class Food:
    def __init__(self):
        self.pos = self._random_pos(exclude=set())

    @staticmethod
    def _random_pos(exclude: set) -> Tuple[int, int]:
        while True:
            pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if pos not in exclude:
                return pos

    def respawn(self, occupied: List[Tuple[int, int]]):
        self.pos = self._random_pos(exclude=set(occupied))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.reset()

    def reset(self):
        start = (GRID_COLS // 2, GRID_ROWS // 2)
        self.snake = Snake(start)
        self.food = Food()
        # Ensure food doesn't spawn on snake
        self.food.respawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.paused = False

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self):
        for i, (cx, cy) in enumerate(self.snake.body):
            rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GREEN if i == 0 else (0, 160, 0)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_food(self):
        cx, cy = self.food.pos
        rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_hud(self):
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))
        if self.paused and not self.game_over:
            overlay = self.big_font.render("Paused (P to resume)", True, BLUE)
            self.screen.blit(overlay, overlay.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        if self.game_over:
            over = self.big_font.render("Game Over! Press R to Restart", True, WHITE)
            self.screen.blit(over, over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.snake.set_direction(UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.snake.set_direction(DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.snake.set_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.set_direction(RIGHT)
                elif event.key == pygame.K_p:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()

    def update(self):
        if self.game_over or self.paused:
            return
        self.snake.move()
        # Collisions
        if self.snake.hits_wall() or self.snake.hits_self():
            self.game_over = True
            return
        # Eat food
        if self.snake.body[0] == self.food.pos:
            self.score += 1
            self.snake.grow(1)
            self.food.respawn(self.snake.body)

    def draw(self):
        self.screen.fill((20, 20, 20))
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
