const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const particles = [];
for (let i = 0; i < 50; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2 + 1,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        alpha: Math.random() * 0.5 + 0.1
    });
}
function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(220, 38, 38, ${p.alpha})`;
        ctx.fill();
    });
    requestAnimationFrame(drawParticles);
}
drawParticles();
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});
let currentGrid = null;
let currentPath = null;
let agentPos = null;
let targetPos = null;
let startPos = null;
let gameState = 'setup';
let stepInterval = null;
let userScore = 0;
let aiScore = 0;
let currentRound = 0;
let totalRounds = 5;
const mazeContainer = document.getElementById('maze-container');
const btnStart = document.getElementById('btn-start');
const btnRules = document.getElementById('btn-rules');
const btnCloseRules = document.getElementById('btn-close-rules');
const btnNextRound = document.getElementById('btn-next-round');
const btnPlayAgain = document.getElementById('btn-play-again');
const rulesModal = document.getElementById('rules-modal');
const endModal = document.getElementById('end-modal');
const resultOverlay = document.getElementById('result-overlay');
const resultIcon = document.getElementById('result-icon');
const resultText = document.getElementById('result-text');
const inputRounds = document.getElementById('setup-rounds');
const sliderGridSize = document.getElementById('setup-grid-size');
const sliderComplexity = document.getElementById('setup-complexity');
const sliderSpeed = document.getElementById('setup-speed');
const valGridSize = document.getElementById('setup-grid-val');
const valComplexity = document.getElementById('setup-complexity-val');
const valSpeed = document.getElementById('setup-speed-val');
const scoreYou = document.getElementById('score-you');
const scoreAi = document.getElementById('score-ai');
const hudRound = document.getElementById('hud-round');
const hudStatus = document.getElementById('hud-status');
const hudStatusText = document.getElementById('hud-status-text');
const stepCurrent = document.getElementById('game-steps');
const stepLimit = document.getElementById('game-step-limit');
const aiWinQuotes = [
    "Agent Putin strikes again. 82% accuracy is no joke.",
    "Target acquired. Agent Putin's pathfinding is perfect.",
    "Too easy for Agent Putin. Try a harder maze?",
    "Agent Putin navigated that blindfolded.",
    "Math wins. You never stood a chance against Agent Putin."
];
const playerWinQuotes = [
    "Agent Putin lost your trail! You survived.",
    "Incredible evasion! The KGB is baffled.",
    "You slipped right through their fingers.",
    "Agent Putin is stuck. You win this round!",
    "Ghost protocol successful. You remain hidden."
];
btnRules.addEventListener('click', () => rulesModal.classList.remove('hidden'));
btnCloseRules.addEventListener('click', () => rulesModal.classList.add('hidden'));
sliderGridSize.addEventListener('input', (e) => {
    valGridSize.textContent = e.target.value;
    if (gameState === 'setup') generateMaze();
});
sliderComplexity.addEventListener('input', (e) => {
    valComplexity.textContent = e.target.value + '%';
    if (gameState === 'setup') generateMaze();
});
sliderSpeed.addEventListener('input', (e) => {
    valSpeed.textContent = e.target.value + 'ms';
});
btnStart.addEventListener('click', () => {
    const roundsVal = parseInt(inputRounds.value);
    if (isNaN(roundsVal) || roundsVal < 1) {
        alert("Please enter a valid number of rounds.");
        return;
    }
    totalRounds = roundsVal;
    inputRounds.disabled = true;
    btnStart.disabled = true;
    userScore = 0;
    aiScore = 0;
    currentRound = 1;
    updateScores();
    updateRoundDisplay();
    generateMaze();
    setStatus('running', 'Select a hideout to begin round');
});
btnNextRound.addEventListener('click', () => {
    resultOverlay.classList.add('hidden');
    if (currentRound >= totalRounds) {
        endTournament();
    } else {
        currentRound++;
        updateRoundDisplay();
        generateMaze();
        setStatus('running', 'Select a hideout for next round');
    }
});
btnPlayAgain.addEventListener('click', () => {
    endModal.classList.add('hidden');
    inputRounds.disabled = false;
    btnStart.disabled = false;
    userScore = 0;
    aiScore = 0;
    currentRound = 0;
    updateScores();
    updateRoundDisplay();
    gameState = 'setup';
    generateMaze();
    setStatus('idle', 'Ready to start');
});
function updateScores() {
    scoreYou.textContent = userScore;
    scoreAi.textContent = aiScore;
}
function updateRoundDisplay() {
    if (currentRound === 0) {
        hudRound.textContent = `0 / 0`;
    } else {
        hudRound.textContent = `${currentRound} / ${totalRounds}`;
    }
}
function endTournament() {
    gameState = 'tournament_end';
    endModal.classList.remove('hidden');
    document.getElementById('end-score-you').textContent = userScore;
    document.getElementById('end-score-ai').textContent = aiScore;
    const endIcon = document.getElementById('end-icon');
    const endTitle = document.getElementById('end-title');
    const endSubtitle = document.getElementById('end-subtitle');
    endIcon.className = 'end-icon';
    if (userScore > aiScore) {
        endIcon.classList.add('win');
        endIcon.innerHTML = '<i class="fa-solid fa-trophy"></i>';
        endTitle.textContent = 'MISSION ACCOMPLISHED';
        endSubtitle.textContent = `You were able to breach the security of Agent Putin! (${userScore}–${aiScore})`;
    } else if (aiScore > userScore) {
        endIcon.classList.add('lose');
        endIcon.innerHTML = '<i class="fa-solid fa-robot"></i>';
        endTitle.textContent = 'AGENT PUTIN WINS!';
        endSubtitle.textContent = `You were captured ${aiScore}–${userScore}.`;
    } else {
        endIcon.classList.add('draw');
        endIcon.innerHTML = '<i class="fa-solid fa-handshake"></i>';
        endTitle.textContent = 'STALEMATE';
        endSubtitle.textContent = `It's a tie at ${userScore}–${aiScore}.`;
    }
}
function setStatus(type, text) {
    hudStatus.className = `hud-status ${type}`;
    hudStatusText.textContent = text;
}
function showOverlay(playerWon, text) {
    resultIcon.className = playerWon ? 'fa-solid fa-face-smile' : 'fa-solid fa-robot';
    resultText.textContent = text;
    resultOverlay.className = `result-overlay ${playerWon ? 'success-overlay' : 'failed-overlay'}`;
}
async function generateMaze() {
    if (gameState === 'animating') return;
    if (currentRound > 0 && gameState !== 'tournament_end') {
        gameState = 'playing';
    }
    resultOverlay.classList.add('hidden');
    const size = sliderGridSize.value;
    const complexity = sliderComplexity.value / 100;
    mazeContainer.style.gridTemplateColumns = `repeat(${size}, minmax(0, 1fr))`;
    mazeContainer.style.gridTemplateRows = `repeat(${size}, minmax(0, 1fr))`;
    let iconSize = '1rem';
    if (size > 20) iconSize = '0.6rem';
    else if (size > 15) iconSize = '0.8rem';
    mazeContainer.style.fontSize = iconSize;
    try {
        const response = await fetch(`/api/generate?row=${size}&col=${size}&wall_prob=${complexity}`);
        const data = await response.json();
        currentGrid = data.maze;
        startPos = data.start;
        agentPos = [...startPos];
        targetPos = null;
        stepCurrent.textContent = '0';
        stepLimit.textContent = Math.floor((size * size) * 0.75);
        renderMaze();
    } catch (error) {
        console.error("Failed to generate maze:", error);
        setStatus('failed', 'Connection error');
    }
}
function renderMaze() {
    mazeContainer.innerHTML = '';
    for (let r = 0; r < currentGrid.length; r++) {
        for (let c = 0; c < currentGrid[r].length; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            if (currentGrid[r][c] === 1 || currentGrid[r][c] === 'x') {
                cell.classList.add('wall');
            } else {
                if (r === startPos[0] && c === startPos[1]) {
                    cell.classList.add('start');
                    cell.innerHTML = '<i class="fa-solid fa-robot"></i>';
                }
                if (gameState === 'playing') {
                    cell.classList.add('reachable');
                    cell.addEventListener('click', () => selectTarget(r, c));
                }
            }
            cell.dataset.r = r;
            cell.dataset.c = c;
            mazeContainer.appendChild(cell);
        }
    }
}
function getCell(r, c) {
    return mazeContainer.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`);
}
function selectTarget(r, c) {
    if (gameState !== 'playing' || currentGrid[r][c] === 1 || currentGrid[r][c] === 'x') return;
    if (r === startPos[0] && c === startPos[1]) return;
    targetPos = [r, c];
    const cell = getCell(r, c);
    cell.classList.add('goal');
    cell.innerHTML = '<i class="fa-solid fa-crosshairs"></i>';
    document.querySelectorAll('.cell.reachable').forEach(el => {
        el.classList.remove('reachable');
        el.classList.add('unreachable');
    });
    runAI();
}
async function runAI() {
    gameState = 'animating';
    setStatus('running', 'Agent Putin is tracking you...');
    let current_pos = startPos;
    let step_count = 0;
    let prev_act_x = 0.0;
    let prev_act_y = 0.0;
    let visited_counts = {};
    let total_reward = 0.0;
    const size = parseInt(sliderGridSize.value);
    const maxSteps = parseInt(stepLimit.textContent);
    const speed = parseInt(sliderSpeed.value);
    const startCell = getCell(startPos[0], startPos[1]);
    startCell.classList.remove('start');
    startCell.innerHTML = '';
    while (true) {
        try {
            const response = await fetch('/api/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    maze: currentGrid,
                    row: size,
                    col: size,
                    current_pos: current_pos,
                    goal_pos: targetPos,
                    step_count: step_count,
                    prev_act_x: prev_act_x,
                    prev_act_y: prev_act_y,
                    visited_counts: visited_counts,
                    total_reward: total_reward
                })
            });
            const data = await response.json();
            if (step_count > 0 || current_pos !== startPos) {
                const prevCell = getCell(current_pos[0], current_pos[1]);
                prevCell.classList.remove('agent');
                prevCell.classList.add('path');
                prevCell.innerHTML = '';
            }
            if (data.next_pos) {
                current_pos = data.next_pos;
                step_count = data.step_count;
                prev_act_x = data.prev_act_x;
                prev_act_y = data.prev_act_y;
                visited_counts = data.visited_counts;
                total_reward = data.total_reward;
                const currCell = getCell(current_pos[0], current_pos[1]);
                currCell.classList.add('agent');
                currCell.innerHTML = '<i class="fa-solid fa-robot"></i>';
                stepCurrent.textContent = step_count;
            }
            if (data.done || step_count >= maxSteps || !data.next_pos) {
                if (data.success || (current_pos[0] === targetPos[0] && current_pos[1] === targetPos[1])) {
                    aiScore++;
                    updateScores();
                    const quote = aiWinQuotes[Math.floor(Math.random() * aiWinQuotes.length)];
                    showOverlay(false, `Agent Putin found you in ${step_count} steps!`);
                    setStatus('failed', quote);
                } else {
                    userScore++;
                    updateScores();
                    const quote = playerWinQuotes[Math.floor(Math.random() * playerWinQuotes.length)];
                    if (step_count >= maxSteps) {
                        showOverlay(true, `You Win! Agent Putin exceeded max steps.`);
                    } else {
                        showOverlay(true, `Agent Putin got lost!`);
                    }
                    setStatus('success', quote);
                }
                gameState = 'round_end';
                break;
            }
            await new Promise(r => setTimeout(r, speed));
        } catch (error) {
            console.error("AI Error:", error);
            setStatus('failed', 'Error communicating with Agent Putin');
            gameState = 'round_end';
            break;
        }
    }
}
generateMaze();
updateRoundDisplay();
