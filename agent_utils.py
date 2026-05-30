import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
def generate_grid(row, column, start_random=False):
  obs = ['.','.','.','.','x']
  grid = np.array([[obs[random.randint(0,len(obs)-1)] for i in range(column)] for i in range(row)])
  g_x , g_y = random.randint(0,row-1), random.randint(0,column-1)
  grid[g_x][g_y] = 'G'
  x_start = random.randint(0,row-1)
  y_start = random.randint(0,column-1)
  if start_random:
    while (grid[x_start][y_start] == 'G' or grid[x_start][y_start] == 'x'):
      x_start = random.randint(0,row-1)
      y_start = random.randint(0,column-1)
  else:
    grid[0][0] = 'S'
  grid[x_start][y_start] = 'S'
  return grid
def visualize_maze(maze_data):
    mapping = {'S': 0, 'G': 1, 'x': 2, '.': 3}
    numeric_grid = np.array([[mapping[cell] for cell in row] for row in maze_data])
    plt.figure(figsize=(6, 10))
    colors = ["#32CD32", "#FF4500", "#000000", "#F8F8FF"]
    sns.heatmap(numeric_grid, cmap=colors, cbar=False,
                linewidths=0.5, linecolor='black', square=True)
    plt.axis('off')
    plt.show()
def find_pos(symbol, row ,col, grid):
  for i in range(row):
    for j in range(col):
      if grid[i][j] == symbol:
        return (i,j)
from collections import deque
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
row,col= 10,10
maze = generate_grid(row,col, True)
g_pos = find_pos('G', row,col, maze)
start_pos = find_pos('S', row,col,maze)
print(f'Total cells: {row*col}')
print(f'Pos of G = {g_pos}')
print(f"is solvable : {is_solvable(maze,start_pos,g_pos)}")
visualize_maze(maze)
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
        norm = d
        distances.append(norm)
    return distances 
get_distances(maze,find_pos('S',row,col,maze))
agent_x , agent_y = find_pos('S',row,col,maze)
goal_x, goal_y = find_pos('G', row,col,maze)
wall_up, wall_down, wall_left, wall_right = get_distances(maze,(agent_x,agent_y))
goal_dist = abs(agent_x-goal_x) + abs(goal_y - agent_y)
prev_act_x, prev_act_y = 0.0, 0.0
is_stuck = 0.0
is_looping = 0.0
history = []
norm_goal_dist = goal_dist / (row + col)
norm_up, norm_down, norm_left, norm_right = [w/max(row, col) for w in [wall_up, wall_down, wall_left, wall_right]]
rel_goal_x = (goal_x - agent_x) / col
rel_goal_y = (goal_y - agent_y) / row
state = np.array([
    rel_goal_x, rel_goal_y,          
    norm_up, norm_down,              
    norm_left, norm_right,           
    prev_act_x, prev_act_y,          
    float(is_stuck),                 
    float(is_looping),               
    norm_goal_dist,                  
], dtype=np.float32)
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
  dx,dy = action_map[action]
  new_x = current_pos[0]+dx
  new_y = current_pos[1]+dy
  return(new_x, new_y)
def step(maze, current_pos, action, goal_pos):
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
def reset():
    maze = generate_grid(row, col, True)
    goal_pos = find_pos("G", row, col, maze)
    start_pos = find_pos("S", row ,col, maze)
    current_pos = start_pos
    is_stuck = 0.0
    is_looping = 0.0
    history = []
    prev_act_x, prev_act_y = 0.0, 0.0
    return maze, current_pos, goal_pos, is_stuck, is_looping, history, prev_act_x, prev_act_y
import numpy as np
import random
def select_action(state, model, epsilon):
    if random.random() < epsilon:
        return random.randint(0, 3)
    else:
        q_values = model.predict(state.reshape(1, 12), verbose=0)
        return np.argmax(q_values)
import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
def build_model(state_size =12, action_size=4):
  model = Sequential([
      Input(shape=(state_size,)),
      Dense(units=256,activation='relu'),
      Dense(units=128,activation='relu'),
      Dense(units=64,activation='relu'),
      Dense(units=4,activation='linear')
  ])
  model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
  return model
model=build_model()
model.summary()
from collections import deque
import random
import numpy as np
replay_buffer = deque(maxlen=20000)
def store_experience(state, action, reward, next_state, done):
    replay_buffer.append((state, action, reward, next_state, done))
def get_batch(batch_size=64):
    batch = random.sample(replay_buffer, batch_size)
    states, actions, rewards, next_states, dones = zip(*batch)
    return (
        np.array(states, dtype=np.float32),
        np.array(actions, dtype=np.int32),
        np.array(rewards, dtype=np.float32),
        np.array(next_states, dtype=np.float32),
        np.array(dones, dtype=np.bool_)
    )
def train_step(model, batch_size, gamma=0.95):
    if len(replay_buffer) < batch_size:
        return
    states, actions, rewards, next_states, dones = get_batch(batch_size)
    targets = model.predict(states, verbose=0)
    next_q_values = model.predict(next_states, verbose=0)
    for i in range(batch_size):
        if dones[i]:
            targets[i][actions[i]] = rewards[i]
        else:
            targets[i][actions[i]] = rewards[i] + gamma * np.max(next_q_values[i])
    model.fit(states, targets, epochs=1, verbose=0)
def run_training(episodes, batch_size, row, col):
    epsilon = 1.0
    epsilon_min = 0.01
    epsilon_decay = 0.995
    success_count = 0
    MAX_STEPS = 200 
    for episode in range(episodes):
        maze, current_pos, goal_pos, is_stuck, is_looping, history, prev_act_x, prev_act_y = reset()
        start_pos = current_pos
        min_possible_steps = abs(goal_pos[0] - start_pos[0]) + abs(goal_pos[1] - start_pos[1])
        step_count = 0
        done = False
        total_reward = 0
        while not done and step_count < MAX_STEPS:
            state = get_state(maze, current_pos, goal_pos, is_stuck, is_looping,
                              history, prev_act_x, prev_act_y, step_count, row, col)
            if np.random.rand() < epsilon:
                action = np.random.randint(0, 4)
            else:
                q_values = model(state.reshape(1, -1), training=False)
                action = np.argmax(q_values[0].numpy())
            next_pos, reward, done = step(maze, current_pos, action, goal_pos)
            if next_pos == goal_pos:
                success_count += 1
            next_state = get_state(maze, next_pos, goal_pos, is_stuck, is_looping,
                                   history, prev_act_x, prev_act_y, step_count + 1, row, col)
            store_experience(state, action, reward, next_state, done)
            if len(replay_buffer) >= batch_size and step_count % 4 == 0:
                train_step(model, batch_size)
            current_pos = next_pos
            total_reward += reward
            step_count += 1
            prev_act_x, prev_act_y = action_map[action]
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay
        optimality_ratio = step_count / min_possible_steps if min_possible_steps > 0 else 1.0
        print(f"{episode+1} | Start: {start_pos} | Goal: {goal_pos} | Steps: {step_count} (Min: {min_possible_steps}) | Reward: {total_reward:.1f} | Successes: {success_count} | Epsilon: {epsilon:.4f}")
run_training(episodes=1000, batch_size=64, row=row, col=col)
def print_maze_with_path(maze, path, goal_pos):
    visual_grid = maze.copy()
    for (r, c) in path:
        if (r, c) != goal_pos:
            visual_grid[r, c] = '*'
    print("\n--- Agent Path Visualization ---")
    for r in range(visual_grid.shape[0]):
        print(" ".join(visual_grid[r]))
    print("--------------------------------\n")
def test_and_visualize(model, row, col):
    maze = generate_grid(row, col, start_random=True)
    current_pos = find_pos("S", row,col,maze)
    goal_pos = find_pos("G", row,col,maze)
    path = [current_pos]
    done = False
    step_count = 0
    total_reward = 0
    print(f"Testing on new maze | Start: {current_pos} | Goal: {goal_pos}")
    while not done and step_count < 100:
        state = get_state(maze, current_pos, goal_pos, False, False, [], 0, 0, step_count, row, col)
        q_values = model(state.reshape(1, -1), training=False)
        action = np.argmax(q_values[0].numpy())
        next_pos, reward, done = step(maze, current_pos, action, goal_pos)
        path.append(next_pos)
        current_pos = next_pos
        total_reward += reward
        step_count += 1
    print_maze_with_path(maze, path, goal_pos)
    print(f"Result: {'SUCCESS' if next_pos == goal_pos else 'FAILED'} | Steps: {step_count} | Reward: {total_reward:.1f}")
suuccess = 0
for i in range(10):
  test_and_visualize(model, row=10, col=10)
