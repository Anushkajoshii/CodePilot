// script.js
// Simple calculator implementation

// DOM References
const display = document.getElementById('display');
const buttons = document.querySelectorAll('.btn');

// Calculator state
let currentOperand = '';
let previousOperand = '';
let operation = null;

/**
 * Append a digit or decimal point to the current operand.
 * @param {string} number - The digit or '.' to append.
 */
function appendNumber(number) {
  // Prevent multiple decimals
  if (number === '.' && currentOperand.includes('.')) return;

  // Prevent malformed leading zeros (e.g., "00", "01")
  if (currentOperand === '0' && number !== '.') {
    // Replace leading zero with the new digit (typical calculator behaviour)
    currentOperand = number;
    return;
  }

  // Normal case – concatenate
  currentOperand = currentOperand + number;
}

/**
 * Choose an operation (+, -, *, /).
 * Stores the current operand as previous and prepares for the next input.
 * @param {string} op - The operator symbol.
 */
function chooseOperation(op) {
  if (currentOperand === '' && previousOperand === '') return; // nothing to operate on

  // If we already have a pending operation and both operands exist, compute first
  if (previousOperand !== '' && currentOperand !== '') {
    compute();
  }

  // Move current to previous if present
  if (currentOperand !== '') {
    previousOperand = currentOperand;
    currentOperand = '';
  }
  operation = op;
}

/**
 * Perform the calculation based on stored operands and operation.
 */
function compute() {
  if (operation === null || previousOperand === '' || currentOperand === '') {
    return; // insufficient data
  }

  const prev = parseFloat(previousOperand);
  const current = parseFloat(currentOperand);
  let result;

  // Guard division by zero
  if (operation === '/' && current === 0) {
    // Show error and reset state (but keep error visible until cleared)
    display.textContent = 'Error';
    currentOperand = 'Error';
    previousOperand = '';
    operation = null;
    return;
  }

  switch (operation) {
    case '+':
      result = prev + current;
      break;
    case '-':
      result = prev - current;
      break;
    case '*':
      result = prev * current;
      break;
    case '/':
      result = prev / current;
      break;
    default:
      return;
  }

  // Store result as the new current operand
  currentOperand = Number.isFinite(result) ? result.toString() : 'Error';
  previousOperand = '';
  operation = null;
}

/**
 * Update the calculator display.
 */
function updateDisplay() {
  display.textContent = currentOperand || previousOperand || '0';
}

/**
 * Reset the calculator to its initial state.
 */
function clearAll() {
  currentOperand = '';
  previousOperand = '';
  operation = null;
  updateDisplay();
}

/**
 * Delete the last character of the current operand.
 */
function deleteLast() {
  if (currentOperand && currentOperand !== 'Error') {
    currentOperand = currentOperand.slice(0, -1);
  }
  updateDisplay();
}

// Attach event listeners to all buttons
buttons.forEach(button => {
  button.addEventListener('click', () => {
    const type = button.dataset.type;
    const value = button.dataset.value;

    switch (type) {
      case 'digit':
        // If an error is displayed, start fresh
        if (currentOperand === 'Error') clearAll();
        appendNumber(value);
        break;
      case 'operator':
        if (currentOperand === 'Error') clearAll();
        chooseOperation(value);
        break;
      case 'action':
        if (value === 'C') {
          clearAll();
        } else if (value === '←') {
          deleteLast();
        } else if (value === '=') {
          compute();
        }
        break;
      default:
        // No action for unknown types
        break;
    }

    // Update display after handling the button (compute already updates state)
    updateDisplay();
  });
});

// Export functions for potential unit testing
window.calculator = {
  appendNumber,
  chooseOperation,
  compute,
  clearAll,
  deleteLast,
  updateDisplay,
  getState: () => ({ currentOperand, previousOperand, operation })
};
