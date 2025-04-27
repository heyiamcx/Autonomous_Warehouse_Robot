import pygame
import random
import heapq  # For A* pathfinding

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
ORANGE = (255, 165, 0)  # For urgent packages

# Display setup
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Warehouse Simulation")

# Grid setup
shelves = [(x, y) for x in range(2, 18) for y in [1, 2, 4, 5, 7, 8] if x not in [9, 10]]
pickup_points = [(19, 2), (19, 5), (19, 8)]
delivery_points = [(0, 2), (0, 5), (0, 8)]
charging_stations = [(1,0), (1,9), (18, 0), (18, 9)]

# Initialize shelf inventory: some shelves are empty
shelf_inventory = {}
targeted_empty_shelves = set()
assigned_red_shelves = set()
initial_empty_count = int(len(shelves) * 0.3)
initial_empty = set(random.sample(shelves, initial_empty_count))
for shelf in shelves:
    shelf_inventory[shelf] = {
        'status': 'empty' if shelf in initial_empty else 'full',
        'urgent': False
    }

# Pickup point packages
pickup_packages = {point: 1 for point in pickup_points}

# Robots
num_robots = 4
pink_robots = [{'pos': list(random.choice(pickup_points)), 'task': 'restock', 'target_shelf': None,
                'carrying': False, 'step': None, 'battery': random.randint(50, 100), 'charging': False, 
                'charging_station': None, 'wait_counter': 0, 'id': f'pink{i}', 'path': []} for i in range(num_robots)]
green_robots = [{'pos': list(random.choice(delivery_points)), 'task': 'idle', 'carrying': False,
                 'target_shelf': None, 'battery': random.randint(50, 100), 'charging': False, 
                 'charging_station': None, 'wait_counter': 0, 'id': f'green{i}', 'path': []} for i in range(num_robots)]

# In-transit packages
in_transit_packages = []

# Periodically mark shelves for delivery
multi_red_cooldown = 0

def mark_shelves_for_delivery():
    global multi_red_cooldown
    if multi_red_cooldown <= 0:
        eligible = [s for s in shelves if shelf_inventory[s]['status'] == 'full' and s not in assigned_red_shelves]
        num_to_mark = min(3, len(eligible))
        if num_to_mark > 0:
            for shelf in random.sample(eligible, num_to_mark):
                shelf_inventory[shelf]['status'] = 'target'
                shelf_inventory[shelf]['urgent'] = random.random() < 0.5  # 50% chance of being urgent
            multi_red_cooldown = 20
    else:
        multi_red_cooldown -= 1

# Green robot logic with priority for urgent

def assign_green_robot_task(robot):
    urgent_targets = [s for s in shelves if shelf_inventory[s] == 'target' and shelf_inventory.get(s, {}).get('urgent')]
    normal_targets = [s for s in shelves if shelf_inventory[s] == 'target' and not shelf_inventory.get(s, {}).get('urgent')]

    if urgent_targets:
        robot['target_shelf'] = random.choice(urgent_targets)
    elif normal_targets:
        robot['target_shelf'] = random.choice(normal_targets)
    else:
        return False

    assigned_red_shelves.add(robot['target_shelf'])
    robot['task'] = 'pickup'
    return True

def is_position_occupied(pos, all_robots):
    """Check if a position is occupied by any robot"""
    return any(tuple(robot['pos']) == tuple(pos) for robot in all_robots)

def is_valid_move(current_pos, new_pos, robot, all_robots, shelves):
    """
    Check if the move is valid (not colliding with other robots or shelves)
    """
    # Convert positions to tuples for comparison
    current_pos = tuple(current_pos)
    new_pos = tuple(new_pos)
    
    # Check boundaries
    if new_pos[0] < 0 or new_pos[0] >= GRID_SIZE[0] or new_pos[1] < 0 or new_pos[1] >= GRID_SIZE[1]:
        return False
    
    # Check for robot collisions
    all_positions = [tuple(r['pos']) for r in all_robots if r['id'] != robot['id']]
    if new_pos in all_positions:
        return False
    
    # Special handling for shelf access
    if new_pos in shelves:
        # Allow movement to shelf only if it's the specific target shelf for this robot
        target_shelf = robot.get('target_shelf')
        if target_shelf is not None and new_pos == tuple(target_shelf):
            return True
        return False
    
    return True

def manhattan_distance(a, b):
    """Calculate Manhattan distance between two points"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path(start, goal, robot, all_robots, shelves):
    """A* pathfinding algorithm"""
    # If the goal is a shelf that's not the target, find an adjacent position
    if tuple(goal) in shelves and tuple(goal) != robot.get('target_shelf'):
        # Find adjacent positions to the shelf
        x, y = goal
        adjacent_positions = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        valid_adjacent = [pos for pos in adjacent_positions 
                         if 0 <= pos[0] < GRID_SIZE[0] and 0 <= pos[1] < GRID_SIZE[1] 
                         and pos not in shelves]
        if valid_adjacent:
            goal = min(valid_adjacent, key=lambda pos: manhattan_distance(start, pos))
    
    # A* algorithm
    open_set = []
    heapq.heappush(open_set, (0, tuple(start)))
    came_from = {}
    g_score = {tuple(start): 0}
    f_score = {tuple(start): manhattan_distance(start, goal)}
    closed_set = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        if current == tuple(goal):
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return [list(p) for p in path][1:]  # Skip the start position
        
        # Check neighbors
        x, y = current
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        for neighbor in neighbors:
            if not is_valid_move(current, neighbor, robot, all_robots, shelves):
                continue
                
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # No path found, return empty path
    return []

def find_nearest_charging_station(pos):
    occupied = {tuple(robot['charging_station']) for robot in pink_robots + green_robots
                if robot['charging_station'] is not None and robot['task'] == 'charge'}
    available = [cs for cs in charging_stations if cs not in occupied]
    if available:
        return min(available, key=lambda cs: abs(pos[0] - cs[0]) + abs(pos[1] - cs[1]))
    else:
        return min(charging_stations, key=lambda cs: abs(pos[0] - cs[0]) + abs(pos[1] - cs[1]))

def draw_grid():
    screen.fill(WHITE)
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if (x, y) in shelves:
                pygame.draw.rect(screen, YELLOW, rect)

    # Draw pickup points
    for p in pickup_points:
        pygame.draw.rect(screen, GRAY, pygame.Rect(p[0] * CELL_SIZE, p[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        if pickup_packages[p] > 0:
            pkg_rect = pygame.Rect(p[0] * CELL_SIZE + CELL_SIZE // 4,
                                   p[1] * CELL_SIZE + CELL_SIZE // 4,
                                   CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.rect(screen, BROWN, pkg_rect)

    # Draw delivery points
    for d in delivery_points:
        pygame.draw.rect(screen, BLUE, pygame.Rect(d[0] * CELL_SIZE, d[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw charging stations
    for cs in charging_stations:
        pygame.draw.rect(screen, CYAN, pygame.Rect(cs[0] * CELL_SIZE, cs[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    font = pygame.font.SysFont(None, 20)

    # Draw pink robots (restockers)
    for pr in pink_robots:
        x, y = pr['pos']
        pygame.draw.circle(screen, PINK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        battery_text = font.render(f"{pr['battery']}%", True, BLACK)
        text_rect = battery_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2 - CELL_SIZE // 2.2))
        screen.blit(battery_text, text_rect)

    # Draw green robots (deliverers)
    for gr in green_robots:
        x, y = gr['pos']
        pygame.draw.circle(screen, GREEN, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        battery_text = font.render(f"{gr['battery']}%", True, BLACK)
        text_rect = battery_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2 - CELL_SIZE // 2.2))
        screen.blit(battery_text, text_rect)
        
    # Draw shelf contents
    for shelf, info in shelf_inventory.items():
        if info['status'] == 'full':
            color = BROWN
        elif info['status'] == 'target':
            color = ORANGE if info.get('urgent') else RED
        else:
            continue

        rect = pygame.Rect(shelf[0] * CELL_SIZE + CELL_SIZE // 4,
                           shelf[1] * CELL_SIZE + CELL_SIZE // 4,
                           CELL_SIZE // 2, CELL_SIZE // 2)
        pygame.draw.rect(screen, color, rect)

        if info['status'] == 'target' and info.get('urgent'):
            urgent_label = font.render('URG', True, BLACK)
            screen.blit(urgent_label, (shelf[0] * CELL_SIZE + 3, shelf[1] * CELL_SIZE + 3))

    # Draw packages in transit
    for pkg in in_transit_packages:
        offset_y = -5 if pkg['carried_by'] else 0
        rect = pygame.Rect(pkg['pos'][0] * CELL_SIZE + CELL_SIZE // 4,
                           pkg['pos'][1] * CELL_SIZE + CELL_SIZE // 4 + offset_y,
                           CELL_SIZE // 2, CELL_SIZE // 2)
        pygame.draw.rect(screen, BROWN, rect)

def handle_battery(robot, all_robots):
    """Manage robot battery levels and charging"""
    # Discharge battery when not charging
    if not robot['charging']:
        robot['battery'] = max(0, robot['battery'] - 1)
        # Check if battery is low and robot needs to charge
        if robot['battery'] <= 20 and robot['charging_station'] is None:
            # Save current task to resume after charging
            robot['prev_task'] = robot['task']
            robot['prev_step'] = robot.get('step')
            robot['task'] = 'charge'
            robot['charging_station'] = find_nearest_charging_station(robot['pos'])
            robot['path'] = find_path(robot['pos'], robot['charging_station'], robot, all_robots, shelves)

    # Handle charging state
    if robot['task'] == 'charge':
        if robot['pos'] == list(robot['charging_station']):
            # At charging station, charge up
            robot['charging'] = True
            robot['battery'] += 5
            if robot['battery'] >= 100:
                # Fully charged, resume previous task
                robot['battery'] = 100
                robot['charging'] = False
                robot['task'] = robot.pop('prev_task', 'idle')
                if 'prev_step' in robot:
                    robot['step'] = robot.pop('prev_step', None)
                robot['charging_station'] = None
                robot['path'] = []
        elif robot['path']:
            # Move towards charging station
            robot['pos'] = robot['path'].pop(0)
        else:
            # If path is empty, recalculate
            robot['path'] = find_path(robot['pos'], robot['charging_station'], robot, all_robots, shelves)
            if robot['path']:
                robot['pos'] = robot['path'].pop(0)
            else:
                # If still no path, wait
                robot['wait_counter'] = 3

def move_robot(robot, target, all_robots, shelves):
    """Move robot towards target using pathfinding"""
    # If waiting, decrement counter and stay in place
    if robot['wait_counter'] > 0:
        robot['wait_counter'] -= 1
        return
    
    # If we have a path, follow it
    if robot['path']:
        next_pos = robot['path'][0]
        # Verify the next position is still valid
        if is_valid_move(robot['pos'], next_pos, robot, all_robots, shelves):
            robot['pos'] = robot['path'].pop(0)
        else:
            # Recalculate path if next position is invalid
            robot['path'] = find_path(robot['pos'], target, robot, all_robots, shelves)
    else:
        # Calculate a new path
        robot['path'] = find_path(robot['pos'], target, robot, all_robots, shelves)
        if robot['path']:
            robot['pos'] = robot['path'].pop(0)
        else:
            # If no path is available, wait for a few cycles
            robot['wait_counter'] = 3

def update_packages():
    """Update the positions of packages being carried by robots"""
    for pkg in in_transit_packages:
        if pkg['carried_by']:
            pkg['pos'] = list(pkg['carried_by']['pos'])

running = True
clock = pygame.time.Clock()
pickup_regen_timer = 0
multi_red_cooldown = 0

while running:
    clock.tick(5)  # Frame rate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Regenerate packages at pickup points
    pickup_regen_timer += 1
    if pickup_regen_timer >= 10:
        for p in pickup_points:
            if pickup_packages[p] < 1:
                pickup_packages[p] += 1
        pickup_regen_timer = 0

    all_robots = pink_robots + green_robots

    # First handle battery for all robots
    for robot in all_robots:
        handle_battery(robot, all_robots)

    # Handle pink robots (restockers)
    for robot in pink_robots:
        if robot['task'] == 'charge':
            continue

        if robot['task'] == 'restock' and robot['target_shelf'] is None:
            available = [s for s in shelves if shelf_inventory[s]['status'] == 'empty' and s not in targeted_empty_shelves]
            if available:
                robot['target_shelf'] = random.choice(available)
                robot['pickup_point'] = random.choice(pickup_points)
                robot['step'] = 'to_pickup'
                targeted_empty_shelves.add(robot['target_shelf'])
                robot['path'] = find_path(robot['pos'], robot['pickup_point'], robot, all_robots, shelves)

        if robot['step'] == 'to_pickup':
            if robot['pos'] == list(robot['pickup_point']):
                if pickup_packages[tuple(robot['pickup_point'])] > 0:
                    pickup_packages[tuple(robot['pickup_point'])] -= 1
                    robot['carrying'] = True
                    robot['step'] = 'to_shelf'
                    in_transit_packages.append({'pos': list(robot['pos']), 'carried_by': robot})
                    robot['path'] = find_path(robot['pos'], robot['target_shelf'], robot, all_robots, shelves)
            else:
                move_robot(robot, robot['pickup_point'], all_robots, shelves)

        elif robot['step'] == 'to_shelf':
            if robot['pos'] == list(robot['target_shelf']):
                robot['carrying'] = False
                shelf_inventory[tuple(robot['target_shelf'])]['status'] = 'full'
                shelf_inventory[tuple(robot['target_shelf'])]['urgent'] = False
                targeted_empty_shelves.discard(tuple(robot['target_shelf']))
                in_transit_packages[:] = [pkg for pkg in in_transit_packages if pkg['carried_by'] != robot]
                robot['target_shelf'] = None
                robot['step'] = None
                robot['path'] = []
            else:
                move_robot(robot, robot['target_shelf'], all_robots, shelves)

    # Periodically mark shelves for delivery
    if multi_red_cooldown <= 0:
        eligible = [s for s in shelves if shelf_inventory[s]['status'] == 'full' and s not in assigned_red_shelves]
        num_to_mark = min(3, len(eligible))
        for shelf in random.sample(eligible, num_to_mark):
            shelf_inventory[shelf]['status'] = 'target'
            shelf_inventory[shelf]['urgent'] = random.random() < 0.5
        multi_red_cooldown = 20
    else:
        multi_red_cooldown -= 1

    # Handle green robots (deliverers)
    for robot in green_robots:
        if robot['task'] == 'charge':
            continue

        if robot['task'] == 'idle':
            urgent_targets = [s for s in shelves if shelf_inventory[s]['status'] == 'target'
                      and shelf_inventory[s].get('urgent') and s not in assigned_red_shelves]
            normal_targets = [s for s in shelves if shelf_inventory[s]['status'] == 'target'
                            and not shelf_inventory[s].get('urgent') and s not in assigned_red_shelves]
            
            if urgent_targets:
                robot['target_shelf'] = random.choice(urgent_targets)
            elif normal_targets:
                robot['target_shelf'] = random.choice(normal_targets)
            else:
                continue

            assigned_red_shelves.add(robot['target_shelf'])
            robot['task'] = 'pickup'
            robot['path'] = find_path(robot['pos'], robot['target_shelf'], robot, all_robots, shelves)

        if robot['task'] == 'pickup':
            if robot['pos'] == list(robot['target_shelf']):
                robot['carrying'] = True
                robot['task'] = 'deliver'
                shelf_inventory[tuple(robot['target_shelf'])]['status'] = 'empty'
                shelf_inventory[tuple(robot['target_shelf'])]['urgent'] = False
                assigned_red_shelves.discard(robot['target_shelf'])
                in_transit_packages.append({'pos': list(robot['pos']), 'carried_by': robot})
                robot['delivery_point'] = random.choice(delivery_points)
                robot['path'] = find_path(robot['pos'], robot['delivery_point'], robot, all_robots, shelves)
            else:
                move_robot(robot, robot['target_shelf'], all_robots, shelves)

        elif robot['task'] == 'deliver':
            if robot['pos'] == list(robot['delivery_point']):
                robot['carrying'] = False
                in_transit_packages[:] = [pkg for pkg in in_transit_packages if pkg['carried_by'] != robot]
                robot['task'] = 'idle'
                robot['target_shelf'] = None
                robot['delivery_point'] = None
                robot['path'] = []
            else:
                move_robot(robot, robot['delivery_point'], all_robots, shelves)

    update_packages()
    draw_grid()
    pygame.display.flip()

pygame.quit()
