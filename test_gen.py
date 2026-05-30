import random
import numpy as np

def generate_grid(row, column, start_random=False, wall_prob=0.2):
    grid = np.full((row, column), '.')
    
    num_cells = row * column
    num_walls = int(num_cells * wall_prob)
    
    all_indices = list(range(num_cells))
    wall_indices = random.sample(all_indices, num_walls)
    
    for idx in wall_indices:
        r, c = divmod(idx, column)
        grid[r, c] = 'x'
    
    g_x, g_y = random.randint(0, row-1), random.randint(0, column-1)
    grid[g_x, g_y] = 'G'
    
    x_start = random.randint(0, row-1)
    y_start = random.randint(0, column-1)
    if start_random:
        while (grid[x_start, y_start] == 'G' or grid[x_start, y_start] == 'x'):
            x_start = random.randint(0, row-1)
            y_start = random.randint(0, column-1)
    else:
        grid[0, 0] = 'S'
        x_start, y_start = 0, 0
        
    grid[x_start, y_start] = 'S'
    return grid

print((generate_grid(10, 10, start_random=True, wall_prob=0.2) == 'x').sum())
