// app.js - Core logic for ColorfulTodo
// This script implements task management, persistence, UI rendering, filtering,
// drag‑and‑drop reordering, theme toggling, and keyboard shortcuts.

(() => {
  // ---------- Utility ----------
  const generateId = () => {
    if (typeof crypto !== "undefined" && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    // Fallback simple UUID v4 generator
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  };

  // ---------- Model ----------
  class Task {
    constructor(text) {
      this.id = generateId();
      this.text = text;
      this.completed = false;
      this.createdAt = new Date().toISOString();
    }
  }

  const state = {
    tasks: [],
    filter: "all", // all | active | completed
    isDarkMode: false,
  };

  // ---------- Persistence ----------
  const TASKS_KEY = "colorfulTodoTasks";
  const THEME_KEY = "colorfulTodoTheme";

  const loadTasks = () => {
    const raw = localStorage.getItem(TASKS_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        // Ensure each item has required properties (basic validation)
        if (Array.isArray(parsed)) {
          state.tasks = parsed.map(t => ({
            id: t.id,
            text: t.text,
            completed: !!t.completed,
            createdAt: t.createdAt || new Date().toISOString(),
          }));
        }
      } catch (e) {
        console.error("Failed to parse tasks from localStorage", e);
      }
    }
  };

  const saveTasks = () => {
    try {
      localStorage.setItem(TASKS_KEY, JSON.stringify(state.tasks));
    } catch (e) {
      console.error("Failed to save tasks", e);
    }
  };

  const loadTheme = () => {
    const theme = localStorage.getItem(THEME_KEY);
    state.isDarkMode = theme === "dark";
    document.body.classList.toggle("dark-mode", state.isDarkMode);
  };

  const saveTheme = () => {
    const value = state.isDarkMode ? "dark" : "light";
    localStorage.setItem(THEME_KEY, value);
  };

  // ---------- Rendering ----------
  const taskListEl = document.getElementById("task-list");

  const clearTaskList = () => {
    while (taskListEl.firstChild) taskListEl.removeChild(taskListEl.firstChild);
  };

  const createTaskElement = (task) => {
    const li = document.createElement("li");
    li.className = "task-item";
    if (task.completed) li.classList.add("completed");
    li.setAttribute("data-id", task.id);
    li.setAttribute("draggable", "true");

    // Checkbox
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.completed;
    checkbox.className = "task-checkbox";
    checkbox.addEventListener("change", () => toggleComplete(task.id));

    // Label (text)
    const label = document.createElement("span");
    label.className = "task-text";
    label.textContent = task.text;

    // Edit button
    const editBtn = document.createElement("button");
    editBtn.className = "edit-btn";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => {
      const newText = prompt("Edit task", task.text);
      if (newText !== null) editTask(task.id, newText.trim());
    });

    // Delete button
    const delBtn = document.createElement("button");
    delBtn.className = "delete-btn";
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", () => deleteTask(task.id));

    // Assemble
    li.appendChild(checkbox);
    li.appendChild(label);
    li.appendChild(editBtn);
    li.appendChild(delBtn);

    // Drag‑and‑drop events for this li
    li.addEventListener("dragstart", onDragStart);
    li.addEventListener("dragend", onDragEnd);

    return li;
  };

  const renderTasks = () => {
    clearTaskList();
    const filtered = state.tasks.filter(task => {
      if (state.filter === "active") return !task.completed;
      if (state.filter === "completed") return task.completed;
      return true; // all
    });
    filtered.forEach(task => {
      const el = createTaskElement(task);
      taskListEl.appendChild(el);
    });
    updateFilterButtons();
  };

  // ---------- CRUD ----------
  const addTask = (text) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    const newTask = new Task(trimmed);
    state.tasks.push(newTask);
    saveTasks();
    renderTasks();
  };

  const editTask = (id, newText) => {
    const task = state.tasks.find(t => t.id === id);
    if (!task) return;
    task.text = newText.trim() || task.text;
    saveTasks();
    renderTasks();
  };

  const deleteTask = (id) => {
    state.tasks = state.tasks.filter(t => t.id !== id);
    saveTasks();
    renderTasks();
  };

  const toggleComplete = (id) => {
    const task = state.tasks.find(t => t.id === id);
    if (!task) return;
    task.completed = !task.completed;
    saveTasks();
    renderTasks();
  };

  // ---------- Filtering ----------
  const setFilter = (filter) => {
    if (["all", "active", "completed"].includes(filter)) {
      state.filter = filter;
      renderTasks();
    }
  };

  const updateFilterButtons = () => {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      const btnFilter = btn.dataset.filter;
      const isActive = btnFilter === state.filter;
      btn.setAttribute('aria-pressed', isActive);
      btn.classList.toggle('active', isActive);
    });
  };

  // ---------- Theme ----------
  const toggleTheme = () => {
    state.isDarkMode = !state.isDarkMode;
    document.body.classList.toggle('dark-mode', state.isDarkMode);
    saveTheme();
  };

  // ---------- Drag and Drop ----------
  let draggedId = null;

  function onDragStart(e) {
    draggedId = this.dataset.id;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", draggedId);
    this.classList.add("dragging");
  }

  function onDragEnd() {
    this.classList.remove("dragging");
    draggedId = null;
  }

  const onDragOver = (e) => {
    e.preventDefault(); // necessary to allow drop
    const afterElement = getDragAfterElement(taskListEl, e.clientY);
    const draggingEl = taskListEl.querySelector('.dragging');
    if (!draggingEl) return;
    if (afterElement == null) {
      taskListEl.appendChild(draggingEl);
    } else {
      taskListEl.insertBefore(draggingEl, afterElement);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    const idsInDomOrder = Array.from(taskListEl.children).map(li => li.dataset.id);
    // Reorder state.tasks to match idsInDomOrder while preserving other tasks not displayed due to filter
    const reordered = [];
    idsInDomOrder.forEach(id => {
      const task = state.tasks.find(t => t.id === id);
      if (task) reordered.push(task);
    });
    // Append tasks that were filtered out (keep original order)
    state.tasks.forEach(t => {
      if (!reordered.includes(t)) reordered.push(t);
    });
    state.tasks = reordered;
    saveTasks();
    renderTasks();
  };

  // Helper: find element after which the dragged item should be placed
  function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-item:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
  }

  // ---------- Keyboard shortcuts ----------
  const onDocumentKeyDown = (e) => {
    const activeEl = document.activeElement;
    const isInputFocused = activeEl && (activeEl.id === "new-task" || activeEl.tagName === "INPUT" || activeEl.isContentEditable);
    // Ctrl+Shift+L for theme toggle
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "l") {
      e.preventDefault();
      toggleTheme();
      return;
    }
    if (!isInputFocused && e.key === "Enter") {
      // Focus the new‑task input
      e.preventDefault();
      document.getElementById("new-task").focus();
    }
    if (isInputFocused && e.key === "Enter") {
      e.preventDefault();
      const input = document.getElementById("new-task");
      addTask(input.value);
      input.value = "";
    }
  };

  // ---------- Event Listeners (DOMContentLoaded) ----------
  document.addEventListener("DOMContentLoaded", () => {
    // Load persisted data
    loadTasks();
    loadTheme();
    renderTasks();

    // Add button
    const addBtn = document.getElementById("add-btn");
    const newTaskInput = document.getElementById("new-task");
    addBtn.addEventListener("click", () => {
      addTask(newTaskInput.value);
      newTaskInput.value = "";
    });
    // Enter key on input handled globally (see onDocumentKeyDown)

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        setFilter(btn.dataset.filter);
      });
    });

    // Clear completed
    const clearBtn = document.getElementById("clear-completed");
    clearBtn.addEventListener('click', () => {
      state.tasks = state.tasks.filter(t => !t.completed);
      saveTasks();
      renderTasks();
    });

    // Theme toggle
    const themeToggle = document.getElementById("theme-toggle");
    themeToggle.addEventListener('click', toggleTheme);

    // Drag and drop on the list container
    taskListEl.addEventListener('dragover', onDragOver);
    taskListEl.addEventListener('drop', onDrop);

    // Global keyboard shortcuts
    document.addEventListener('keydown', onDocumentKeyDown);
  });
})();
