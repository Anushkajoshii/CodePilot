// script.js
// Simple calculator implementation
// This script defines a Calculator class handling display updates, input processing,
// operator selection, calculation, clearing, and keyboard support.

/**
 * Calculator class encapsulating the calculator logic.
 */
class Calculator {
  /**
   * @param {HTMLInputElement} displayElement - The input element used as the display.
   */
  constructor(displayElement) {
    /** @type {HTMLInputElement} */
    this.displayElement = displayElement;
    this.currentInput = "0"; // start with 0 displayed
    this.previousValue = null; // stored numeric value before an operator
    this.operator = null; // current operator (+, -, *, /)
    this.resetNext = false; // flag to reset input on next digit entry
    this.updateDisplay();
  }

  /**
   * Append a digit (or decimal point) to the current input.
   * @param {string} digit
   */
  appendDigit(digit) {
    if (this.resetNext) {
      // Start fresh after an operator or a calculation
      this.currentInput = digit === "." ? "0." : digit;
      this.resetNext = false;
    } else {
      // Prevent multiple leading zeros
      if (this.currentInput === "0" && digit !== ".") {
        this.currentInput = digit;
      } else if (digit === "." && this.currentInput.includes('.')) {
        // ignore additional decimal points
      } else {
        this.currentInput += digit;
      }
    }
    this.updateDisplay();
  }

  /**
   * Choose an operator (+, -, *, /). Stores the current value and prepares for next input.
   * @param {string} op
   */
  chooseOperator(op) {
    const currentNumber = parseFloat(this.currentInput);
    if (this.previousValue === null) {
      this.previousValue = currentNumber;
    } else if (this.operator) {
      // If an operator was already selected, compute intermediate result first
      const result = this._performOperation(this.previousValue, currentNumber, this.operator);
      if (result === null) {
        // Division by zero handled inside _performOperation
        this.currentInput = "Error";
        this.updateDisplay();
        this._resetAll();
        return;
      }
      this.previousValue = result;
      this.currentInput = String(result);
    }
    this.operator = op;
    this.resetNext = true;
    this.updateDisplay();
  }

  /**
   * Perform the calculation based on the stored operator and values.
   */
  calculate() {
    if (!this.operator || this.previousValue === null) {
      // Nothing to calculate
      return;
    }
    const currentNumber = parseFloat(this.currentInput);
    const result = this._performOperation(this.previousValue, currentNumber, this.operator);
    if (result === null) {
      // Division by zero
      this.currentInput = "Error";
    } else {
      this.currentInput = String(result);
    }
    this.updateDisplay();
    // Reset state after calculation
    this._resetAll();
    this.resetNext = true; // allow new entry after result
  }

  /**
   * Clear the calculator to its initial state.
   */
  clear() {
    this.currentInput = "0";
    this._resetAll();
    this.updateDisplay();
  }

  /**
   * Write the current input to the display element.
   */
  updateDisplay() {
    this.displayElement.value = this.currentInput;
  }

  // ---------- Private helper methods ----------

  /**
   * Reset stored values except the current input (used after clear or after a successful calculation).
   */
  _resetAll() {
    this.previousValue = null;
    this.operator = null;
    this.resetNext = false;
  }

  /**
   * Perform a binary operation.
   * @param {number} a
   * @param {number} b
   * @param {string} op
   * @returns {number|null} - Returns null for division by zero.
   */
  _performOperation(a, b, op) {
    switch (op) {
      case "+":
        return a + b;
      case "-":
        return a - b;
      case "*":
        return a * b;
      case "/":
        if (b === 0) return null;
        return a / b;
      default:
        return b; // fallback (should not happen)
    }
  }
}

// Instantiate the calculator with the display element from the DOM.
const calculator = new Calculator(document.getElementById('display'));
// Expose globally for potential future extensions.
window.calculator = calculator;

// Attach click event listeners to all calculator buttons.
document.querySelectorAll('button').forEach((button) => {
  const action = button.dataset.action;
  const value = button.dataset.value; // used for digits and operators

  button.addEventListener('click', () => {
    switch (action) {
      case 'digit':
        calculator.appendDigit(value);
        break;
      case 'operator':
        calculator.chooseOperator(value);
        break;
      case 'equals':
        calculator.calculate();
        break;
      case 'clear':
        calculator.clear();
        break;
      default:
        // No action needed
        break;
    }
  });
});

// Keyboard support – map physical keys to button clicks.
document.addEventListener('keydown', (event) => {
  let key = event.key;
  // Normalise some keys to match data-key attributes.
  if (key === 'Enter') key = 'Enter';
  if (key === 'Escape' || key === 'Backspace') key = 'Escape';
  // For Numpad keys, the event.key already returns the digit or operator.
  const button = document.querySelector(`button[data-key="${key}"]`);
  if (button) {
    button.click();
    event.preventDefault();
  }
});
