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
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)

# Display setup
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Warehouse Simulation")

# Grid setup
shelves = [(x, y) for x in range(2, 18) for y in [1, 2, 4, 5, 7, 8] if x not in [9, 10]]
pickup_points = [(19, 2), (19, 5), (19, 8)]
delivery_points = [(0, 2), (0, 5), (0, 8)]
charging_stations = [(18, 0), (18, 9)]

# Initialize shelf inventory: some shelves are empty
shelf_inventory = {}
targeted_empty_shelves = set()
assigned_red_shelves = set()
initial_empty_count = int(len(shelves) * 0.3)
initial_empty = set(random.sample(shelves, initial_empty_count))
for shelf in shelves:
    shelf_inventory[shelf] = 'empty' if shelf in initial_empty else 'full'

# Pickup point packages
pickup_packages = {point: 1 for point in pickup_points}

# Robots
num_robots = 4
pink_robots = [{'pos': list(random.choice(pickup_points)), 'task': 'restock', 'target_shelf': None,
                'carrying': False, 'step': None, 'battery': random.randint(20, 100), 'charging': False, 'charging_station': None} for _ in range(num_robots)]
green_robots = [{'pos': list(random.choice(delivery_points)), 'task': 'idle', 'carrying': False,
                 'target_shelf': None, 'battery': random.randint(20, 100), 'charging': False, 'charging_station': None} for _ in range(num_robots)]

# In-transit packages
in_transit_packages = []

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
        if pickup_packages[p] > 0:
            pkg_rect = pygame.Rect(p[0] * CELL_SIZE + CELL_SIZE // 4,
                                   p[1] * CELL_SIZE + CELL_SIZE // 4,
                                   CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.rect(screen, BROWN, pkg_rect)

    for d in delivery_points:
        pygame.draw.rect(screen, BLUE, pygame.Rect(d[0] * CELL_SIZE, d[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for cs in charging_stations:
        pygame.draw.rect(screen, CYAN, pygame.Rect(cs[0] * CELL_SIZE, cs[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    font = pygame.font.SysFont(None, 20)

    for pr in pink_robots:
        x, y = pr['pos']
        pygame.draw.circle(screen, PINK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        battery_text = font.render(f"{pr['battery']}%", True, BLACK)
        screen.blit(battery_text, (x * CELL_SIZE + 5, y * CELL_SIZE + 5))

    for gr in green_robots:
        x, y = gr['pos']
        pygame.draw.circle(screen, GREEN, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        battery_text = font.render(f"{gr['battery']}%", True, BLACK)
        screen.blit(battery_text, (x * CELL_SIZE + 5, y * CELL_SIZE + 5))

    for shelf, status in shelf_inventory.items():
        if status == 'full':
            color = BROWN
        elif status == 'target':
            color = RED
        else:
            continue
        rect = pygame.Rect(shelf[0] * CELL_SIZE + CELL_SIZE // 4,
                           shelf[1] * CELL_SIZE + CELL_SIZE // 4,
                           CELL_SIZE // 2, CELL_SIZE // 2)
        pygame.draw.rect(screen, color, rect)

    for pkg in in_transit_packages:
        offset_y = -5 if pkg['carried_by'] else 0
        rect = pygame.Rect(pkg['pos'][0] * CELL_SIZE + CELL_SIZE // 4,
                           pkg['pos'][1] * CELL_SIZE + CELL_SIZE // 4 + offset_y,
                           CELL_SIZE // 2, CELL_SIZE // 2)
        pygame.draw.rect(screen, BROWN, rect)

def move_towards(current, target):
    cx, cy = current
    tx, ty = target
    if cx < tx:
        cx += 1
    elif cx > tx:
        cx -= 1
    elif cy < ty:
        cy += 1
    elif cy > ty:
        cy -= 1
    return [cx, cy]

def find_nearest_charging_station(pos):
    return min(charging_stations, key=lambda cs: abs(cs[0] - pos[0]) + abs(cs[1] - pos[1]))

def handle_battery(robot):
    if not robot['charging']:
        robot['battery'] = max(0, robot['battery'] - 1)
        if robot['battery'] <= 10 and robot['charging_station'] is None:
            robot['prev_task'] = robot['task']
            robot['prev_step'] = robot.get('step')
            robot['task'] = 'charge'
            robot['charging_station'] = find_nearest_charging_station(robot['pos'])

    if robot['task'] == 'charge':
        if robot['pos'] == list(robot['charging_station']):
            robot['charging'] = True
            robot['battery'] += 5
            if robot['battery'] >= 100:
                robot['battery'] = 100
                robot['charging'] = False
                robot['task'] = robot.pop('prev_task')
                if 'prev_step' in robot:
                    robot['step'] = robot.pop('prev_step')
                robot['charging_station'] = None
        else:
            robot['pos'] = move_towards(robot['pos'], robot['charging_station'])

running = True
clock = pygame.time.Clock()
pickup_regen_timer = 0
multi_red_cooldown = 0

while running:
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pickup_regen_timer += 1
    if pickup_regen_timer >= 10:
        for p in pickup_points:
            if pickup_packages[p] < 1:
                pickup_packages[p] += 1
        pickup_regen_timer = 0

    for robot in pink_robots + green_robots:
        handle_battery(robot)

    for robot in pink_robots:
        if robot['task'] == 'charge':
            continue
        if robot['task'] == 'restock' and robot['target_shelf'] is None:
            available = [s for s in shelves if shelf_inventory[s] == 'empty' and s not in targeted_empty_shelves]
            if available:
                robot['target_shelf'] = random.choice(available)
                robot['pickup_point'] = random.choice(pickup_points)
                robot['step'] = 'to_pickup'
                targeted_empty_shelves.add(robot['target_shelf'])

        if robot['step'] == 'to_pickup':
            if robot['pos'] == list(robot['pickup_point']):
                if pickup_packages[tuple(robot['pickup_point'])] > 0:
                    pickup_packages[tuple(robot['pickup_point'])] -= 1
                    robot['carrying'] = True
                    robot['step'] = 'to_shelf'
                    in_transit_packages.append({'pos': list(robot['pos']), 'carried_by': robot})
            else:
                robot['pos'] = move_towards(robot['pos'], robot['pickup_point'])

        elif robot['step'] == 'to_shelf':
            if robot['pos'] == list(robot['target_shelf']):
                robot['carrying'] = False
                shelf_inventory[tuple(robot['target_shelf'])] = 'full'
                targeted_empty_shelves.discard(tuple(robot['target_shelf']))
                in_transit_packages = [pkg for pkg in in_transit_packages if pkg['carried_by'] != robot]
                robot['target_shelf'] = None
                robot['step'] = None
            else:
                robot['pos'] = move_towards(robot['pos'], robot['target_shelf'])
                for pkg in in_transit_packages:
                    if pkg['carried_by'] == robot:
                        pkg['pos'] = list(robot['pos'])

    if multi_red_cooldown == 0:
        eligible = [s for s in shelves if shelf_inventory[s] == 'full']
        num_to_mark = min(3, len(eligible))
        for shelf in random.sample(eligible, num_to_mark):
            shelf_inventory[shelf] = 'target'
        multi_red_cooldown = 20
    else:
        multi_red_cooldown -= 1

    for robot in green_robots:
        if robot['task'] == 'charge':
            continue
        if robot['task'] == 'idle':
            targets = [s for s in shelves if shelf_inventory[s] == 'target' and s not in assigned_red_shelves]
            if targets:
                robot['target_shelf'] = random.choice(targets)
                assigned_red_shelves.add(robot['target_shelf'])
                robot['task'] = 'pickup'

        if robot['task'] == 'pickup':
            if robot['pos'] == list(robot['target_shelf']):
                robot['carrying'] = True
                robot['task'] = 'deliver'
                shelf_inventory[tuple(robot['target_shelf'])] = 'empty'
                assigned_red_shelves.discard(robot['target_shelf'])
            else:
                robot['pos'] = move_towards(robot['pos'], robot['target_shelf'])

        elif robot['task'] == 'deliver':
            if robot.get('delivery_point') is None:
                robot['delivery_point'] = random.choice(delivery_points)
            if robot['pos'] == list(robot['delivery_point']):
                robot['carrying'] = False
                robot['task'] = 'idle'
                robot['target_shelf'] = None
                robot['delivery_point'] = None
            else:
                robot['pos'] = move_towards(robot['pos'], robot['delivery_point'])

    draw_grid()
    pygame.display.flip()

pygame.quit()
