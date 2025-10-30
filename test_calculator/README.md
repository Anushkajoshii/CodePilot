# SimpleCalc

**SimpleCalc** is a lightweight, web‑based calculator that runs entirely in the browser. It provides a clean, responsive UI for basic arithmetic operations and supports both mouse clicks and keyboard shortcuts.

---

## Tech Stack
- **HTML** – Structure of the calculator UI.
- **CSS** – Styling, theming, and responsive layout.
- **JavaScript** – Interaction logic, keyboard handling, and expression evaluation.

---

## Features
- Basic arithmetic: addition, subtraction, multiplication, division.
- Clear (C) button to reset the current expression.
- Equals (=) button and **Enter** key to compute the result.
- Keyboard shortcuts for digits (0‑9) and operators (`+`, `-`, `*`, `/`).
- Escape key clears the display.
- Responsive design works on desktop and mobile screens.
- Accessible markup with ARIA labels and focus outlines.

---

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/your‑username/simplecalc.git
   cd simplecalc
   ```
2. **Open the application**
   - Locate the `index.html` file in the project root.
   - Open it in any modern web browser (Chrome, Firefox, Edge, Safari, etc.).
   - No build step, package manager, or server is required – the app runs purely client‑side.

---

## Usage Guide
### Using the UI
- Click the digit buttons (0‑9) to build a number.
- Click an operator button (`+`, `-`, `*`, `/`) to add an operation.
- Press **C** to clear the current expression.
- Press **=** (or click the equals button) to evaluate the expression. The result appears in the display.

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| 0‑9 | Input digit |
| `+` | Add |
| `-` | Subtract |
| `*` | Multiply |
| `/` | Divide |
| `Enter` | Evaluate (equals) |
| `Escape` | Clear |

### Error Handling
- Division by zero or malformed expressions result in the display showing `Error`.
- After an error, any subsequent digit or clear input will reset the calculator.

---

## Contribution Guidelines (Optional)
Contributions are welcome! If you would like to improve SimpleCalc:
1. Fork the repository.
2. Create a new branch for your feature or bug‑fix.
3. Ensure the UI remains accessible and the code follows the existing style.
4. Submit a pull request with a clear description of your changes.

---

## License
[Insert License Here] – e.g., MIT, Apache 2.0, etc.

---

## Screenshot
![Calculator Screenshot](screenshot.png)
