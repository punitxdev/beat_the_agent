import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from rl_environment import generate_grid, find_pos, get_state, step, action_map, is_solvable
from collections import deque
app = Flask(__name__)
CORS(app)
print("Loading Keras Model...")
model = tf.keras.models.load_model('agent_rlm_v2.keras')
def bfs_shortest_path(grid, start, goal):
    """Returns shortest path length or -1 if unsolvable."""
    rows, cols = grid.shape
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == goal:
            return dist
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr,nc] != 'x' and (nr,nc) not in visited:
                visited.add((nr,nc))
                queue.append(((nr,nc), dist+1))
    return -1
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/api/generate', methods=['GET'])
def generate_maze():
    row = int(request.args.get('row', 10))
    col = int(request.args.get('col', 10))
    wall_prob = float(request.args.get('wall_prob', 0.2))
    for _ in range(20):
        maze = generate_grid(row, col, start_random=True, wall_prob=wall_prob)
        start_pos = find_pos('S', row, col, maze)
        goal_pos = find_pos('G', row, col, maze)
        if start_pos and goal_pos and is_solvable(maze, start_pos, goal_pos):
            break
    solvable = is_solvable(maze, start_pos, goal_pos) if start_pos and goal_pos else False
    optimal = bfs_shortest_path(maze, start_pos, goal_pos) if solvable else -1
    return jsonify({
        "maze": maze.tolist(),
        "start": start_pos,
        "goal": goal_pos,
        "row": row,
        "col": col,
        "solvable": solvable,
        "optimal_steps": optimal
    })
@app.route('/api/step', methods=['POST'])
def step_maze():
    data = request.json
    maze = np.array(data.get('maze'))
    row = data.get('row', 10)
    col = data.get('col', 10)
    current_pos = tuple(data.get('current_pos'))
    goal_pos = tuple(data.get('goal_pos'))
    step_count = data.get('step_count', 0)
    prev_act_x = data.get('prev_act_x', 0.0)
    prev_act_y = data.get('prev_act_y', 0.0)
    visited_counts = data.get('visited_counts', {})
    total_reward = data.get('total_reward', 0.0)
    current_pos_str = f"{current_pos[0]},{current_pos[1]}"
    if visited_counts.get(current_pos_str, 0) > 4:
        return jsonify({
            "done": True,
            "success": False,
            "reason": "Stuck in Loop"
        })
    visited_counts[current_pos_str] = visited_counts.get(current_pos_str, 0) + 1
    state = get_state(
        maze=maze, 
        agent_pos=current_pos, 
        goal_pos=goal_pos, 
        is_stuck=0.0, 
        is_looping=0.0, 
        history=[], 
        prev_act_x=prev_act_x, 
        prev_act_y=prev_act_y, 
        step_count=step_count, 
        row=row, 
        col=col
    )
    dr = goal_pos[0] - current_pos[0]
    dc = goal_pos[1] - current_pos[1]
    adjacent_action = None
    if (dr, dc) == (-1, 0):
        adjacent_action = 0  
    elif (dr, dc) == (1, 0):
        adjacent_action = 1  
    elif (dr, dc) == (0, -1):
        adjacent_action = 2  
    elif (dr, dc) == (0, 1):
        adjacent_action = 3  
    if adjacent_action is not None:
        action = adjacent_action
    else:
        q_values = model(state.reshape(1, -1), training=False)
        action = int(np.argmax(q_values[0].numpy()))
    next_pos, reward, env_done = step(maze, current_pos, action, goal_pos, row, col)
    step_count += 1
    total_reward += float(reward)
    dx, dy = action_map[action]
    prev_act_x, prev_act_y = float(dx), float(dy)
    done = env_done or (next_pos == goal_pos) or (step_count >= 100)
    success = (next_pos == goal_pos)
    reason = "Success" if success else ("Max Steps Reached" if step_count >= 100 else "")
    return jsonify({
        "next_pos": next_pos,
        "step_count": step_count,
        "prev_act_x": prev_act_x,
        "prev_act_y": prev_act_y,
        "visited_counts": visited_counts,
        "total_reward": total_reward,
        "done": done,
        "success": success,
        "reason": reason
    })
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
