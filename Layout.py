import pygame
import random
import time

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = (8, 8)
CELL_SIZE = 80
SCREEN_SIZE = (GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 153)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 105, 180)

# Create screen
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Warehouse Simulation")

# Define grid positions
shelves = [(1, 1), (1, 2), (1, 3), (1, 4), (3, 2), (3, 3), (3, 4), (5, 5), (4, 5), (3, 5)]
pickup_point = (7, 6)
delivery_point = [(0, 6), (0, 7)]
robot_pos = list(pickup_point)

# Random shelf targets
red_shelf = random.choice(shelves)
green_shelf = random.choice([s for s in shelves if s != red_shelf])

# Robot states
carrying_package = False
task = "pickup"

def draw_grid():
    screen.fill(WHITE)
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

            if (x, y) in shelves:
                pygame.draw.rect(screen, YELLOW, rect)
            if (x, y) in delivery_point:
                pygame.draw.rect(screen, BLUE, rect)
            if (x, y) == pickup_point:
                pygame.draw.rect(screen, GRAY, rect)
            if (x, y) == red_shelf:
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)
            if (x, y) == green_shelf:
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 3)
    
    pygame.draw.circle(screen, PINK, (robot_pos[0] * CELL_SIZE + CELL_SIZE // 2, robot_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    if carrying_package:
        pygame.draw.polygon(screen, BLACK, [(robot_pos[0] * CELL_SIZE + 20, robot_pos[1] * CELL_SIZE + 60), (robot_pos[0] * CELL_SIZE + 40, robot_pos[1] * CELL_SIZE + 20), (robot_pos[0] * CELL_SIZE + 60, robot_pos[1] * CELL_SIZE + 60)])

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(5)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if task == "pickup":
        if robot_pos == list(pickup_point):
            carrying_package = True
            task = "deliver_red"
        else:
            robot_pos[1] -= 1 if robot_pos[1] > pickup_point[1] else -1 if robot_pos[1] < pickup_point[1] else 0
            robot_pos[0] -= 1 if robot_pos[0] > pickup_point[0] else -1 if robot_pos[0] < pickup_point[0] else 0
    
    elif task == "deliver_red":
        if robot_pos == list(red_shelf):
            carrying_package = False
            task = "pickup_green"
        else:
            robot_pos[1] -= 1 if robot_pos[1] > red_shelf[1] else -1 if robot_pos[1] < red_shelf[1] else 0
            robot_pos[0] -= 1 if robot_pos[0] > red_shelf[0] else -1 if robot_pos[0] < red_shelf[0] else 0
    
    elif task == "pickup_green":
        if robot_pos == list(green_shelf):
            carrying_package = True
            task = "deliver_blue"
        else:
            robot_pos[1] -= 1 if robot_pos[1] > green_shelf[1] else -1 if robot_pos[1] < green_shelf[1] else 0
            robot_pos[0] -= 1 if robot_pos[0] > green_shelf[0] else -1 if robot_pos[0] < green_shelf[0] else 0
    
    elif task == "deliver_blue":
        if robot_pos in delivery_point:
            carrying_package = False
            red_shelf = random.choice(shelves)
            green_shelf = random.choice([s for s in shelves if s != red_shelf])
            task = "pickup"
        else:
            robot_pos[1] -= 1 if robot_pos[1] > delivery_point[0][1] else -1 if robot_pos[1] < delivery_point[0][1] else 0
            robot_pos[0] -= 1 if robot_pos[0] > delivery_point[0][0] else -1 if robot_pos[0] < delivery_point[0][0] else 0

    draw_grid()
    pygame.display.flip()

pygame.quit()
