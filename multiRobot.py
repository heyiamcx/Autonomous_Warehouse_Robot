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
shelves = [(x, y) for x in range(2, 18) for y in [1, 2, 4, 5, 7, 8] if x not in [9, 10]]

# Pickup and delivery points
pickup_points = [(19, 8), (19, 2), (19, 5)]
delivery_points = [(0, 8), (0, 2), (0, 5)]

# Initialize robots
num_robots = 4  # Number of pink and green robots
pink_robots = [{'pos': list(random.choice(pickup_points)), 'task': 'pickup', 'carrying': False} for _ in range(num_robots)]
green_robots = [{'pos': list(random.choice(delivery_points)), 'task': 'wait', 'carrying': False} for _ in range(num_robots)]

# Assign initial shelf targets
red_shelves = {}
for _ in range(num_robots):
    shelf = random.choice(shelves)
    red_shelves[shelf] = RED

def draw_grid():
    screen.fill(WHITE)
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if (x, y) in shelves:
                pygame.draw.rect(screen, YELLOW, rect)
    for p in pickup_points:
        pygame.draw.rect(screen, GRAY, pygame.Rect(p[0] * CELL_SIZE, p[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for d in delivery_points:
        pygame.draw.rect(screen, BLUE, pygame.Rect(d[0] * CELL_SIZE, d[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for rs, color in red_shelves.items():
        pygame.draw.circle(screen, color, (rs[0] * CELL_SIZE + CELL_SIZE // 2, rs[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    for pr in pink_robots:
        pygame.draw.circle(screen, PINK, (pr['pos'][0] * CELL_SIZE + CELL_SIZE // 2, pr['pos'][1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    for gr in green_robots:
        pygame.draw.circle(screen, GREEN, (gr['pos'][0] * CELL_SIZE + CELL_SIZE // 2, gr['pos'][1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

running = True
clock = pygame.time.Clock()
while running:
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for i in range(num_robots):
        if i >= len(red_shelves):
            continue  # Prevent index errors if shelves are reassigned

        # Pink robot logic
        if pink_robots[i]['task'] == 'pickup':
            target = random.choice(pickup_points)
            if pink_robots[i]['pos'] == list(target):
                pink_robots[i]['carrying'] = True
                pink_robots[i]['task'] = 'deliver'
            else:
                px, py = pink_robots[i]['pos']
                tx, ty = target
                pink_robots[i]['pos'] = [px + (tx > px) - (tx < px), py + (ty > py) - (ty < py)]
        elif pink_robots[i]['task'] == 'deliver':
            target = list(red_shelves.keys())[i]
            if pink_robots[i]['pos'] == list(target):
                pink_robots[i]['carrying'] = False
                pink_robots[i]['task'] = 'wait'
                green_robots[i]['task'] = 'pickup'
                red_shelves[target] = GREEN  # Package is ready for pickup
            else:
                px, py = pink_robots[i]['pos']
                tx, ty = target
                pink_robots[i]['pos'] = [px + (tx > px) - (tx < px), py + (ty > py) - (ty < py)]
        elif pink_robots[i]['task'] == 'wait':
            pink_robots[i]['pos'] = list(random.choice(pickup_points))

        # Green robot logic
        if green_robots[i]['task'] == 'pickup':
            target = list(red_shelves.keys())[i]
            if red_shelves[target] == GREEN:
                if green_robots[i]['pos'] == list(target):
                    green_robots[i]['carrying'] = True
                    green_robots[i]['task'] = 'deliver'
                    del red_shelves[target]  # Remove collected package marker
                else:
                    gx, gy = green_robots[i]['pos']
                    tx, ty = target
                    green_robots[i]['pos'] = [gx + (tx > gx) - (tx < gx), gy + (ty > gy) - (ty < gy)]
        elif green_robots[i]['task'] == 'deliver':
            target = random.choice(delivery_points)
            if green_robots[i]['pos'] == list(target):
                green_robots[i]['carrying'] = False
                green_robots[i]['task'] = 'wait'
                new_shelf = random.choice(shelves)
                red_shelves[new_shelf] = RED  # Assign new shelf as red
                pink_robots[i]['task'] = 'pickup'
            else:
                gx, gy = green_robots[i]['pos']
                tx, ty = target
                green_robots[i]['pos'] = [gx + (tx > gx) - (tx < gx), gy + (ty > gy) - (ty < gy)]
        elif green_robots[i]['task'] == 'wait':
            green_robots[i]['pos'] = list(random.choice(delivery_points))

    draw_grid()
    pygame.display.flip()

pygame.quit()
