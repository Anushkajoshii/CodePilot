# SimpleTodoApp

## Brief Description
SimpleTodoApp is a lightweight, client‑side todo list web application. It lets users add, complete, and delete tasks directly in the browser, with all data persisted in `localStorage` so the list survives page reloads and browser restarts. No server, build steps, or external dependencies are required – just open `index.html` and start managing tasks.

---

## Features
- **Add tasks** – type a task description and press **Enter** or click the add button.
- **Mark as complete** – click the checkbox next to a task to toggle its completed state.
- **Delete tasks** – remove a task with the delete (✖) button.
- **Persisted data** – tasks are saved in the browser's `localStorage`, so they remain after closing/reopening the page.
- **Responsive UI** – simple, clean layout that works on desktop and mobile browsers.

---

## Tech Stack Summary
| Layer | Technology |
|-------|------------|
| Markup | HTML5 |
| Styling | CSS3 (Flexbox, custom styles) |
| Logic | Vanilla JavaScript (ES6) |
| Persistence | `localStorage` (Web API) |

---

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SimpleTodoApp.git
   cd SimpleTodoApp
   ```
2. **Open the application**
   - Locate the `index.html` file in the project root.
   - Double‑click it or open it with your browser of choice (Chrome, Firefox, Edge, Safari, etc.).
   - No additional build steps, package managers, or server are required.

---

## Usage Guide
1. **Add a task**
   - Click the input field at the top, type your task description, and press **Enter** or click the **+** button.
2. **Complete a task**
   - Click the checkbox next to a task. The task text will be styled to indicate completion.
3. **Delete a task**
   - Click the **✖** (delete) button on the right side of a task.
4. **Data persistence**
   - All tasks are automatically saved to `localStorage`. When you reload the page or close/reopen the browser, your todo list will be restored.

---

## File Structure Overview
```
SimpleTodoApp/
│
├── index.html          # Main HTML file – loads the UI and links CSS/JS
├── style.css           # Styling for the app (layout, colors, responsive design)
├── app.js              # Core JavaScript – handles UI interactions and localStorage
└── README.md           # Project documentation (this file)
```
- **index.html** – Contains the markup for the todo list, input field, and includes `style.css` and `app.js`.
- **style.css** – Defines the visual appearance, including task list layout, completed‑task styling, and mobile responsiveness.
- **app.js** – Implements the functionality: adding tasks, toggling completion, deleting tasks, and persisting the list using `localStorage`.

---

## Screenshot
> ![SimpleTodoApp Screenshot](./screenshot.png)
> *Replace `screenshot.png` with an actual image of the running app.*

---

## Contribution Guidelines
- **Fork** the repository and create a new branch for your feature or bug fix.
- Follow the existing code style (ES6 syntax, consistent indentation, meaningful variable names).
- Keep the UI simple and avoid adding heavy dependencies.
- Update the README if you introduce new features or change the setup process.
- Submit a pull request with a clear description of your changes.

---

*Happy task managing!*