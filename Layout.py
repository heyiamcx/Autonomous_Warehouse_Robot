import pygame
import random

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = (20, 10)
CELL_SIZE = 50
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
shelves = [(2, 1), (3, 1), (4, 1), (5,1), (6,1), (7,1), (8,1),
           (2, 2), (3, 2), (4, 2), (5,2), (6,2), (7,2), (8,2),
           (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1),
           (11, 2), (12, 2), (13, 2), (14, 2), (15, 2), (16, 2), (17, 2),
           (11, 4), (12, 4), (13, 4), (14, 4), (15, 4), (16, 4), (17, 4),
           (11, 5), (12, 5), (13, 5), (14, 5), (15, 5), (16, 5), (17, 5),
           (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
           (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8),
           (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (17, 7),
           (11, 8), (12, 8), (13, 8), (14, 8), (15, 8), (16, 8), (17, 8)]

# Multiple pickup and delivery points
pickup_points = [(19, 8), (19, 2), (19, 5)]
delivery_points = [(0, 8), (0, 2), (0, 5)]

# Randomly select a red shelf, pickup point, and delivery point
red_shelf = random.choice(shelves)
pickup_point = random.choice(pickup_points)
delivery_point = random.choice(delivery_points)

# Robots' starting positions
pink_robot_pos = list(pickup_point)
green_robot_pos = list(red_shelf)

# Robot states
pink_carrying = False
green_carrying = False
pink_task = "pickup"
green_task = "wait"

def draw_grid():
    screen.fill(WHITE)
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

            if (x, y) in shelves:
                pygame.draw.rect(screen, YELLOW, rect)

    # Draw all pickup points
    for p in pickup_points:
        rect = pygame.Rect(p[0] * CELL_SIZE, p[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GRAY, rect)  # Keep them visible

    # Draw all delivery points
    for d in delivery_points:
        rect = pygame.Rect(d[0] * CELL_SIZE, d[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect)  # Keep them visible

    # Draw red shelf
    rect = pygame.Rect(red_shelf[0] * CELL_SIZE, red_shelf[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)

    # Draw robots
    pygame.draw.circle(screen, PINK, (pink_robot_pos[0] * CELL_SIZE + CELL_SIZE // 2, pink_robot_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    pygame.draw.circle(screen, GREEN, (green_robot_pos[0] * CELL_SIZE + CELL_SIZE // 2, green_robot_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(5)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Pink Robot Logic ---
    if pink_task == "pickup":
        if pink_robot_pos == list(pickup_point):
            pink_carrying = True
            pink_task = "deliver"
        else:
            if pink_robot_pos[1] > pickup_point[1]:
                pink_robot_pos[1] -= 1
            elif pink_robot_pos[1] < pickup_point[1]:
                pink_robot_pos[1] += 1

            if pink_robot_pos[0] > pickup_point[0]:
                pink_robot_pos[0] -= 1
            elif pink_robot_pos[0] < pickup_point[0]:
                pink_robot_pos[0] += 1

    elif pink_task == "deliver":
        if pink_robot_pos == list(red_shelf):
            pink_carrying = False
            pink_task = "wait"
            green_task = "pickup"
        else:
            if pink_robot_pos[1] > red_shelf[1]:
                pink_robot_pos[1] -= 1
            elif pink_robot_pos[1] < red_shelf[1]:
                pink_robot_pos[1] += 1

            if pink_robot_pos[0] > red_shelf[0]:
                pink_robot_pos[0] -= 1
            elif pink_robot_pos[0] < red_shelf[0]:
                pink_robot_pos[0] += 1

    # --- Green Robot Logic ---
    if green_task == "pickup":
        if green_robot_pos == list(red_shelf):
            green_carrying = True
            green_task = "deliver"
        else:
            if green_robot_pos[1] > red_shelf[1]:
                green_robot_pos[1] -= 1
            elif green_robot_pos[1] < red_shelf[1]:
                green_robot_pos[1] += 1

            if green_robot_pos[0] > red_shelf[0]:
                green_robot_pos[0] -= 1
            elif green_robot_pos[0] < red_shelf[0]:
                green_robot_pos[0] += 1

    elif green_task == "deliver":
        if green_robot_pos == list(delivery_point):
            green_carrying = False
            green_task = "wait"
            red_shelf = random.choice(shelves)  # Assign new red shelf
            pickup_point = random.choice(pickup_points)  # New pickup point
            delivery_point = random.choice(delivery_points)  # New delivery point
            pink_task = "pickup"
        else:
            if green_robot_pos[1] > delivery_point[1]:
                green_robot_pos[1] -= 1
            elif green_robot_pos[1] < delivery_point[1]:
                green_robot_pos[1] += 1

            if green_robot_pos[0] > delivery_point[0]:
                green_robot_pos[0] -= 1
            elif green_robot_pos[0] < delivery_point[0]:
                green_robot_pos[0] += 1

    draw_grid()
    pygame.display.flip()

pygame.quit()
