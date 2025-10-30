# Tic Tac Toe Web App

## Project Overview
A simple, interactive Tic‑Tac‑Toe game that runs entirely in the browser. Players take turns clicking on a 3×3 grid to place their marks (X or O). The app detects wins, draws, and provides a reset button to start a new match.

## Features
1. **Responsive 3×3 board** – clickable cells rendered as HTML buttons.
2. **Turn indicator** – displays which player's turn it is.
3. **Win detection** – automatically announces the winning player when three marks line up horizontally, vertically, or diagonally.
4. **Draw detection** – declares a draw when all cells are filled without a winner.
5. **Reset functionality** – a button to clear the board and start a fresh game.
6. **Pure client‑side implementation** – built with only HTML, CSS, and JavaScript; no backend required.

## Tech Stack
- **HTML** – structure of the page and the game board.
- **CSS** – styling for layout, colors, and visual feedback.
- **JavaScript** – core game logic, event handling, and UI updates.

## Setup
1. **Clone the repository**
   ```bash
   git clone <repository‑url>
   cd <repository‑folder>
   ```
2. **Open the game**
   - Open `index.html` in any modern web browser (Chrome, Firefox, Edge, Safari).
   - No additional build steps or server are required.

## Usage
- The game always starts with **Player X**.
- Click an empty cell to place the current player's mark.
- After each move the app checks for a win or a draw:
  - **Win** – a message like "Player X wins!" appears and further moves are disabled.
  - **Draw** – a message "It's a draw!" appears when the board is full with no winner.
- The **Reset Game** button clears the board, resets the turn to X, and re‑enables play.

## Development Notes
- **Core logic** lives in `script.js`. It manages the board state, player turns, win/draw detection, and UI updates.
- `index.html` defines the markup for the board and includes the stylesheet (`style.css`) and script (`script.js`).
- `style.css` handles visual styling; you can modify it to change colors, fonts, or layout.
- The files interact as follows:
  1. `index.html` loads `style.css` for presentation.
  2. `script.js` is loaded with the `defer` attribute, ensuring the DOM is ready before the script runs.
  3. Event listeners in `script.js` bind to the board cells and reset button defined in the HTML.

## License
*This project is provided as a learning example. Replace this placeholder with an appropriate open‑source license if you wish to distribute it.*
