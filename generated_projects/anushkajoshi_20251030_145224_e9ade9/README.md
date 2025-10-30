# SimpleCalculator

**SimpleCalculator** is a lightweight, browser‑based calculator built with plain HTML, CSS, and JavaScript. It provides a clean UI for basic arithmetic operations and runs entirely client‑side – no build tools or server are required.

---

## Features

- **Basic arithmetic** – addition, subtraction, multiplication, division.
- **Clear (C) and backspace (←)** – quickly reset the expression or delete the last character.
- **Decimal support** – enter floating‑point numbers using the `.` button.
- **Error handling** – division by zero is prevented and displays an error message.
- **Responsive layout** – works on desktop and mobile browsers.
- **Zero‑dependency** – pure HTML/CSS/JS, no external libraries.

---

## Tech Stack

- **HTML5** – structure of the calculator and UI elements.
- **CSS3** – styling, grid layout, and responsive design.
- **JavaScript (ES6)** – handling button clicks, evaluating expressions, and updating the display.

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. **Open the application**
   - Locate the `index.html` file in the project root.
   - Open it directly in a web browser (double‑click or `Open With → <browser>`).
   - No build step, package manager, or server is required.

---

## Usage Guide

### UI Layout
- **Display** – The top bar shows the current input or the result. It starts at `0`.
- **Buttons** – Arranged in a grid similar to a physical calculator:
  - **Digits (0‑9)** – Input numbers.
  - **Decimal point (.)** – Add a decimal separator.
  - **Operators (+, -, *, /)** – Choose the arithmetic operation.
  - **Action buttons**:
    - **C** – Clears the entire expression and resets the display to `0`.
    - **←** – Backspace; removes the last character entered.
    - **=** – Evaluates the current expression and shows the result.

### Interaction Flow
1. Click digits to build a number.
2. Press an operator to start a new term.
3. Continue entering numbers/operators as needed.
4. Press `=` to compute the result.
5. Use **C** to start over or **←** to correct a typo.

### Division‑by‑Zero Handling
If the user attempts to divide by zero, the calculator does **not** crash. Instead, the display shows the message:
```
Error: Division by zero
```
The user can then press **C** to clear the error and continue.

---

## Development Notes

- **`index.html`** – Contains the static markup for the calculator, including the display element and all buttons. Each button is annotated with `data-type` and `data-value` attributes, which the JavaScript logic uses to determine its role.
- **`style.css`** – Provides the visual styling, grid layout, and responsive adjustments. The design separates button types (`btn-digit`, `btn-operator`, `btn-action`) for easy theming.
- **`script.js`** – Implements the core functionality:
  - Event delegation for button clicks.
  - State management for the current expression.
  - Safe evaluation using `Function` (or a custom parser) with explicit handling for division by zero.
  - UI updates for the display and error messages.
- **Extensibility** – The code is organized so new features (e.g., parentheses, advanced functions) can be added by extending the button set in HTML and updating the evaluation logic in `script.js`.

---

## License

*This project is released under a placeholder license. Replace this section with the appropriate license text (e.g., MIT, Apache 2.0) when finalizing the project.*
