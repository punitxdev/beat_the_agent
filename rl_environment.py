import random
import numpy as np
from collections import deque
def generate_grid(row, column, start_random=False, wall_prob=0.2):
    num_cells = row * column
    num_walls = int(num_cells * wall_prob)
    grid = np.full((row, column), '.')
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
def find_pos(symbol, row, col, grid):
    for i in range(row):
        for j in range(col):
            if grid[i][j] == symbol:
                return (i, j)
    return None
def is_solvable(grid, start, goal):
    rows, cols = grid.shape
    queue = deque([start])
    visited = {start}
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and               grid[nr, nc] != 'x' and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False
def get_distances(grid, pos):
    r, c = pos
    rows, cols = grid.shape
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
    distances = []
    for dr, dc in directions:
        d = 0
        nr, nc = r + dr, c + dc
        while 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] != 'x':
            d += 1
            nr += dr
            nc += dc
        distances.append(d)
    return distances
def get_state(maze, agent_pos, goal_pos, is_stuck, is_looping, history, prev_act_x, prev_act_y, step_count, row, col):
    agent_x, agent_y = agent_pos
    goal_x, goal_y = goal_pos
    wall_up, wall_down, wall_left, wall_right = get_distances(maze, agent_pos)
    goal_dist = abs(agent_x - goal_x) + abs(goal_y - agent_y)
    norm_goal_dist = goal_dist / (row + col)
    norm_up, norm_down, norm_left, norm_right = [w / max(row, col) for w in [wall_up, wall_down, wall_left, wall_right]]
    rel_goal_x = (goal_x - agent_x) / col
    rel_goal_y = (goal_y - agent_y) / row
    norm_step = min(step_count / (row * col), 1.0)
    return np.array([
        rel_goal_x, rel_goal_y,
        norm_up, norm_down,
        norm_left, norm_right,
        prev_act_x, prev_act_y,
        float(is_stuck), float(is_looping),
        norm_goal_dist, norm_step
    ], dtype=np.float32)
action_map = {
    0: (-1, 0), 
    1: (1, 0),  
    2: (0, -1), 
    3: (0, 1)   
}
def get_next_pos(current_pos, action):
    dx, dy = action_map[action]
    new_x = current_pos[0] + dx
    new_y = current_pos[1] + dy
    return (new_x, new_y)
def step(maze, current_pos, action, goal_pos, row, col):
    new_pos = get_next_pos(current_pos, action)
    x, y = new_pos
    old_dist = abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])
    new_dist = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])
    if x < 0 or x >= row or y < 0 or y >= col:
        return current_pos, -10, False
    if maze[x][y] == 'G':
        return new_pos, 200, True
    if maze[x][y] == 'x':
        return current_pos, -20, False
    move_reward = 1.0 if new_dist < old_dist else -1.0
    return new_pos, move_reward - 0.5, False
