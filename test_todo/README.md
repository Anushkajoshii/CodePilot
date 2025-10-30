# Project Overview

**Demo Application** – A lightweight, interactive web app built with vanilla **HTML**, **CSS**, and **JavaScript**. It showcases a responsive UI with drag‑and‑drop functionality, keyboard shortcuts, a dark/light theme toggle, and persistence of user settings using **localStorage**.

---

## Screenshot

> **[Screenshot Placeholder]**
>
> Insert screenshots of the app here (e.g., `screenshot-desktop.png`, `screenshot-mobile.png`).
>
> ![Desktop View](path/to/desktop-screenshot.png)
> ![Mobile View](path/to/mobile-screenshot.png)
>
---

## Features

- **Drag‑and‑Drop** – Move items around the interface with mouse or touch.
- **Keyboard Shortcuts** – Quick actions via the keyboard (see the table below).
- **Theme Toggle** – Switch between Light and Dark themes; the choice is saved.
- **State Persistence** – All user interactions (theme, layout, etc.) are stored in **localStorage** and restored on reload.
- **Responsive Design** – Works on desktop, tablet, and mobile screens.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Markup | **HTML5** (index.html) |
| Styling | **CSS3** (styles.css) – includes CSS variables for theming |
| Behaviour | **Vanilla JavaScript** (app.js) – no external libraries |

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. **Open the app**
   - Simply open `index.html` in any modern web browser (Chrome, Firefox, Edge, Safari).
   - No build step, server, or package manager is required.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + D` (or `Cmd + D` on macOS) | Toggle **Dark/Light** theme |
| `Ctrl + Z` | Undo the last drag‑and‑drop operation |
| `Ctrl + Y` | Redo the undone operation |
| `Arrow Keys` | Fine‑tune the selected item's position (when an item is focused) |
| `Esc` | Deselect any selected element |

> **Note:** All shortcuts work only when the app is focused (i.e., the browser tab is active).

---

## Drag‑and‑Drop Usage

- Click and hold an item to start dragging.
- Move the cursor (or finger on touch devices) to the desired drop zone.
- Release to drop the item.
- The new position is saved automatically to **localStorage**.

---

## Theme Toggle

- Click the **Theme** button in the top‑right corner or press `Ctrl + D`.
- The selected theme is stored in **localStorage** and applied on subsequent visits.

---

## Folder Structure

```
project-root/
│
├─ index.html          # Main HTML entry point
├─ styles.css          # Global stylesheet (including theme variables)
├─ app.js              # Core JavaScript – handles UI logic, shortcuts, drag‑and‑drop, and persistence
├─ README.md           # Documentation (this file)
└─ assets/            # Optional folder for images, screenshots, icons, etc.
```

- **index.html** – Contains the markup and links to `styles.css` and `app.js`.
- **styles.css** – Defines layout, component styling, and CSS custom properties for light/dark themes.
- **app.js** – Implements all interactive behavior:
  - Event listeners for drag‑and‑drop.
  - Keyboard shortcut handling.
  - Theme switching logic.
  - Persistence via `localStorage` (stores theme, item positions, and any undo/redo stacks).
- **README.md** – Provides users with an overview, usage instructions, and development notes.

---

## Persistence with `localStorage`

The app saves the following data in the browser’s **localStorage** under the key `appState`:

```json
{
  "theme": "light" | "dark",
  "layout": {
    "itemId": { "x": number, "y": number },
    ...
  },
  "undoStack": [...],
  "redoStack": [...]
}
```

- When the page loads, `app.js` reads this object (if present) and restores the UI to the saved state.
- Any change (theme toggle, drag‑and‑drop, undo/redo) updates the stored state immediately, ensuring the user’s preferences persist across sessions.

---

## Contributing

Feel free to fork the repository, make improvements, and submit a pull request. Since the project uses only vanilla web technologies, no additional build tools are required.

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.
