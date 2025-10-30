// Tic Tac Toe game script

// Game state variables
let board = Array(9).fill(null); // Stores 'X', 'O', or null for each cell
let currentPlayer = 'X'; // 'X' starts first
let isGameActive = true; // Flag to control if moves are allowed

// Cache DOM elements
const cells = document.querySelectorAll('.cell');
const statusEl = document.getElementById('status');
const resetBtn = document.getElementById('reset');

// Event listeners
cells.forEach(cell => cell.addEventListener('click', handleCellClick));
resetBtn.addEventListener('click', resetGame);

/**
 * Handles a click on a cell.
 * @param {MouseEvent} event
 */
function handleCellClick(event) {
  if (!isGameActive) return; // Ignore clicks after game over

  const cell = event.target;
  const index = Number(cell.dataset.index);

  // Ignore if cell already taken
  if (board[index]) return;

  // Update state and UI
  board[index] = currentPlayer;
  cell.textContent = currentPlayer;
  cell.classList.add(currentPlayer);

  // Check for win or draw
  if (checkWin()) return;
  if (checkDraw()) return;

  // Switch player
  currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
  statusEl.textContent = `Player ${currentPlayer}'s turn`;
}

/**
 * Checks whether the current board has a winning combination.
 * @returns {boolean} true if a win is detected
 */
function checkWin() {
  const winCombos = [
    [0, 1, 2], // rows
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6], // columns
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8], // diagonals
    [2, 4, 6]
  ];

  for (const combo of winCombos) {
    const [a, b, c] = combo;
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      statusEl.textContent = `Player ${board[a]} wins!`;
      isGameActive = false;
      return true;
    }
  }
  return false;
}

/**
 * Checks for a draw (board full with no winner).
 * @returns {boolean} true if draw detected
 */
function checkDraw() {
  if (board.every(cell => cell !== null) && isGameActive) {
    statusEl.textContent = "It's a draw!";
    isGameActive = false;
    return true;
  }
  return false;
}

/**
 * Resets the game to its initial state.
 */
function resetGame() {
  board = Array(9).fill(null);
  currentPlayer = 'X';
  isGameActive = true;

  cells.forEach(cell => {
    cell.textContent = '';
    cell.classList.remove('X', 'O');
  });

  statusEl.textContent = "Player X's turn";
}
