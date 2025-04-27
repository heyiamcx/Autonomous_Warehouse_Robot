# Autonomous Warehouse Robots
Designing Intelligent Agent Group Coursework

This project simulates an autonomous warehouse environment with multiple pink restocker robots and green delivery robots using Python and Pygame.
Robots move around a grid-based warehouse, picking up, restocking, delivering, and charging dynamically with A* pathfinding, battery management, collision avoidance, and urgent package prioritization.  


### Features
- **Grid-based warehouse layout** (20x10 cells).
- **Pink Robots** :
  -  Pick up packages from pickup points.
  -  Restock empty shelves automatically.
- **Green Robots**:
  - Pick up ready packages from shelves (red/orange targets).
  - Deliver to delivery points.
  - Prioritize urgent deliveries (orange shelves).
- **Battery Management** :
  - Robots automatically move to charging stations when low on battery.
  - Resume tasks after recharging.
- **A\* Pathfinding**:
  - Robots find the shortest route avoiding obstavles and shelves.
- **Collision Avoidance**:
  - Robots do not cross shelves or occupy the same cell.
- **Dynamic Package Management**:
  - Pickup points regenerate packages over time.
  - Shelves are dynamically assigned delivery tasks.
- **Smooth Animation** using Pygame.

### Setup Instructions
1. Clone the repository or download the script:
```
git clone https://github.com/yourusername/warehouse-robot-simulation.git
cd warehouse-robot-simulation
```
2. Install Dependencies -
   Make sure you have Python 3 installed.  
   Install Pygame:
```
pip install pygame
```
3. Run the Simulation :
```
python warehouse_simulation.py
```

### Controls
- **Close the window** to stop the simulation (`X button` or `CTRL + C` in terminal).
- No manual keyboard controls; all robot movements are **autonomous**.

### How It Works
- Warehouse Grid:
  - Yellow cells: shelves
  - Gray cells: pickup points (where packages appear)
  - Blue cells: delivery points
  - Cyan cells: charging stations
 
- Pink Robots (Restockers):
  - Start at pickup points.
  - Pick packages.
  - Delivery to empty shelves.
  - Return to pickup points for next package.
 
- Green Robots (Delivers):
  - Start at delivery points.
  - Pick up "ready" packages from shelves marked **red** or **orange**.
  - Deliver them to delivery points.
 
- Package Management:
  - New packages appear at pickup points every 10 cycles.
  - Some shelves are marked "urgent" (orange) and prioritized for delivery.
 
- Charging:
  - Robots do to the nearest available charging station when battery falls below 20%.
  -  After charging to full, they will continue their previous task.

### Requirements
- Python 3.7+
- pygame  

You can install pygame easily:
```
pip install pygame
```

### Possible Future Improvements
- Add more types of robots with different speeds.
- Improve robot coordination.
- Optimize pathfinding during heavy congestion.
- Display task queues and stats in a sidebar.

### Credits
Created by Yap Jia Yi, Chiew Cui Xuan and Chuah Jia En
Inspired by warehouse automation systems like Amazon Robotics.




