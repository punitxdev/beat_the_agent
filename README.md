# Beat Agent Putin: Deep Reinforcement Learning Maze Simulator

Beat Agent Putin is a high-fidelity, decoupled web application that serves as an interactive testing ground for autonomous navigation. It pits human strategic placement against a Deep Q-Network (DQN) artificial intelligence within a mathematically guaranteed, dynamically generated grid-world topology.

## Architectural Overview

The project is structured around a strict client-server decoupling, ensuring that heavy tensor computations remain entirely isolated from the browser's render thread. This guarantees high frame rates and a seamless user experience during live simulation.

### 1. The Inference Engine (Backend API)
Driven by a Python/Flask architecture, the backend is responsible for topological generation and asynchronous tensor inference.

- **Stochastic Environment Generation (`rl_environment.py`):** The engine dynamically constructs 2D grids parameterized by user-defined wall probabilities. To prevent impossible scenarios, it employs a Breadth-First Search (BFS) graph-traversal algorithm that validates topological solvability before transmitting the environment to the client.
- **Deep Q-Network AI (`agent_utils.py`):** The core intelligence is a Multi-Layer Perceptron (MLP) built with TensorFlow/Keras, featuring a robust 256-128-64 neural architecture. 
- **12-Dimensional State Formulation:** The AI perceives the grid not as pixels, but through a highly engineered 12-dimensional state vector. This includes relative goal vectors, normalized proximity to adjacent walls in four cardinal directions, cyclical loop-detection flags, and temporal constraints (step count decay).
- **Complex Reward Function:** The agent has been trained via Q-learning to maximize a sophisticated reward structure: highly penalizing wall collisions (-20) and out-of-bounds attempts (-10), subtly rewarding distance minimization (+0.5), and heavily incentivizing goal acquisition (+200).

### 2. The Presentation Layer (Frontend)
The interface is engineered using purely native Web Technologies (Vanilla JavaScript, HTML5, CSS3) to eliminate framework bloat and dependency overhead.

- **Dynamic CSS Grid Rendering (`style.css`):** The frontend relies on responsive fractional `minmax(0, 1fr)` grid layouts. This guarantees that whether the environment is a simple 5x5 grid or a massive 25x25 complex, the aspect ratio and dimensional footprint remain perfectly rigid.
- **Asynchronous State Loop (`app.js`):** The JavaScript engine acts as a game-loop controller. It tracks user-agent scores across multiple rounds and orchestrates the animation sequence by executing asynchronous REST API calls (`/api/move`) to fetch the DQN's predicted tensor actions without locking the UI.
- **Thematic Aesthetics:** The dashboard employs a calculated, professional constructivist design. Utilizing a sharp red, white, and blue palette, rigid geometric borders, and authoritative typography, the UI immerses the user in the Cold War "KGB Evasion" narrative.

## Simulation Features

- **Granular Complexity Control:** Users can manipulate the environment's wall density down to exact percentile thresholds, altering the fundamental landscape of the simulation.
- **Real-Time Predictive Visualization:** Observe the internal logic of a trained neural network as it calculates spatial routes, attempts to backtrack out of dead ends, and adjusts its policy on the fly.
- **Temporal Loop Avoidance:** The backend specifically tracks coordinate history to trigger "is_looping" and "is_stuck" penalty flags, forcing the neural network to break out of cyclical pathfinding failures.
- **Persistent Tournament Mode:** A fully tracked round-by-round scoreboard that pits human ingenuity against machine optimization over a continuous session.

## Local Installation and Execution

### System Requirements
- Python 3.8 or higher
- A standard web browser (Chrome/Firefox/Edge)

### Deployment Instructions

1. **Clone the Repository:** Pull the codebase to your local environment.
2. **Initialize a Virtual Environment:** Isolate your dependencies to prevent global package conflicts.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Tensor and Web Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ignite the Server:** Start the Flask inference engine.
   ```bash
   python app.py
   ```

## User Guide

Navigate to `http://localhost:5000` to access the dashboard. 

The objective is strategic placement. Using the control panel on the right, define the grid boundaries, algorithmic speed, and obstacle density. When the round begins, your goal is to select a "Hideout" coordinate that maximizes topological complexity. Try to find the blind spots in the agent's multi-dimensional training space—force it into dead ends, bait it into temporal loops, and outlast its step limit to win the tournament.

## Repository Manifest

- `app.py`: The central Flask router bridging HTTP requests to the neural network.
- `rl_environment.py`: Stochastic grid generation and graph-validation logic.
- `agent_utils.py`: The TensorFlow integration, state-vector formulation, and Q-learning mechanics.
- `static/app.js`: The client-side game loop and asynchronous fetch controller.
- `static/style.css`: The responsive styling engine and thematic design rules.
- `templates/index.html`: The structural DOM and dashboard layout.
- `agent_rlm_v2.keras`: The serialized, pre-trained weights of the Deep Q-Network.
