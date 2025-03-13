import matplotlib.pyplot as plt
import numpy as np

rows, cols = 10, 10  

warehouse = np.zeros((rows, cols))  

shelves = [(2, 2), (2, 3), (2, 6), (2, 7), 
           (5, 2), (5, 3), (5, 6), (5, 7),
           (8, 2), (8, 3), (8, 6), (8, 7)]

for r, c in shelves:
    warehouse[r, c] = 1  

robots = [(3, 4), (6, 5)]
for r, c in robots:
    warehouse[r, c] = 2 

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xticks(np.arange(cols + 1) - 0.5, minor=True)
ax.set_yticks(np.arange(rows + 1) - 0.5, minor=True)
ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

for r in range(rows):
    for c in range(cols):
        if warehouse[r, c] == 1:  
            ax.add_patch(plt.Rectangle((c, rows-r-1), 1, 1, color="purple"))
        elif warehouse[r, c] == 2:  
            ax.add_patch(plt.Circle((c+0.5, rows-r-1+0.5), 0.3, color="orange"))

plt.show()
