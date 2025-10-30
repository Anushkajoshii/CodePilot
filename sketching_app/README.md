# Project Title

**Short Description:**
A lightweight, browser‑based drawing application that lets users sketch with a pen, erase, undo/redo actions, clear the canvas, and download their artwork as an image. No server or build steps required – just open `index.html` in any modern browser.

---

## Screenshot

![Application Screenshot](path/to/screenshot.png) <!-- Replace with actual screenshot -->

---

## Tech Stack
- **HTML** – Structure of the page and canvas element.
- **CSS** – Styling for the toolbar, canvas, and responsive layout.
- **JavaScript** – Core drawing logic, tool handling, undo/redo stack, and download functionality.

---

## Features
- Free‑hand drawing with adjustable pen size and color.
- Eraser tool with adjustable size.
- Undo and redo actions (multiple levels).
- Clear canvas button.
- Download canvas content as a PNG image.
- Simple, responsive UI with a toolbar for all controls.

---

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Open the application**
   - Locate the `index.html` file in the project root.
   - Open it directly in a web browser (Chrome, Firefox, Edge, Safari, etc.).
3. **No build steps or dependencies** are required – the app runs purely client‑side.

---

## Usage Guide
### Toolbar Controls
- **Pen** – Select the pen tool to draw.
- **Eraser** – Switch to the eraser to remove parts of the drawing.
- **Color Picker** – Choose any color for the pen.
- **Size Slider** – Adjust the thickness of the pen or eraser.
- **Undo** – Revert the last drawing action. Can be used repeatedly to step back through the history.
- **Redo** – Re‑apply actions that were undone.
- **Clear** – Remove all strokes from the canvas, resetting it to a blank state.
- **Download** – Save the current canvas as a PNG file to your computer.

### Drawing Workflow
1. Pick a tool (Pen or Eraser) from the toolbar.
2. Choose a color (pen only) and set the desired size.
3. Click and drag on the canvas to draw.
4. Use **Undo**/**Redo** to correct mistakes.
5. When finished, click **Download** to export your artwork.

---

## Development Notes
### File Structure
```
project-root/
│   index.html      # Main HTML entry point
│   styles.css      # Styling for the UI
│   app.js          # Core JavaScript logic (drawing, tools, undo stack)
│   README.md       # Documentation (this file)
```

### Customising Colors & Sizes
- **Pen/Eraser Size:** Controlled by the `<input type="range">` element in `index.html`. The JavaScript reads its value (`strokeWidth`) and applies it to the canvas context.
- **Default Colors:** Defined in `app.js` where the color picker value is initialized. Change the default by modifying the `value` attribute of the `<input type="color">` element.

### Undo/Redo Stack
- The app maintains an array `undoStack` that stores snapshots of the canvas (`ImageData`) after each completed stroke.
- `redoStack` holds snapshots that were undone, allowing redo operations.
- When a new stroke starts, the current canvas state is pushed onto `undoStack` and the `redoStack` is cleared.
- The stack depth is limited only by available memory; you can add a max‑size check if needed.

---

## License
[Insert License Here] – This project is provided as-is for educational purposes. Replace this placeholder with an appropriate open‑source license (e.g., MIT, Apache 2.0) when publishing.
