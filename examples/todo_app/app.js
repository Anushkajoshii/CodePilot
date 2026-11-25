// app.js - Todo application core logic
// State management
let todos = [];

/**
 * Load todos from localStorage into the `todos` array.
 */
function loadTodos() {
    const stored = localStorage.getItem('todos');
    if (stored) {
        try {
            todos = JSON.parse(stored);
        } catch (e) {
            console.error('Failed to parse todos from localStorage', e);
            todos = [];
        }
    } else {
        todos = [];
    }
}

/**
 * Persist the current `todos` array to localStorage.
 */
function saveTodos() {
    localStorage.setItem('todos', JSON.stringify(todos));
}

// DOM references (exported via window for potential external use)
const todoForm = document.getElementById('todo-form');
const newTodoInput = document.getElementById('new-todo');
const todoList = document.getElementById('todo-list');

// expose for testing / external modules (optional)
window.todoForm = todoForm;
window.newTodoInput = newTodoInput;
window.todoList = todoList;
window.loadTodos = loadTodos;
window.saveTodos = saveTodos;
window.renderTodos = renderTodos;
window.handleAddTodo = handleAddTodo;
window.toggleTodo = toggleTodo;
window.deleteTodo = deleteTodo;

/**
 * Render the current list of todos into the DOM.
 */
function renderTodos() {
    // Clear existing list
    todoList.innerHTML = '';

    todos.forEach(todo => {
        const li = document.createElement('li');
        li.className = 'todo-item';

        // Checkbox for completion status
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = todo.completed;
        checkbox.addEventListener('change', () => toggleTodo(todo.id));

        // Text span
        const span = document.createElement('span');
        span.textContent = todo.text;
        if (todo.completed) {
            span.style.textDecoration = 'line-through';
        }

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

        // Assemble list item
        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(deleteBtn);
        todoList.appendChild(li);
    });
}

/**
 * Handle the form submission to add a new todo.
 * @param {Event} event
 */
function handleAddTodo(event) {
    event.preventDefault();
    const text = newTodoInput.value.trim();
    if (!text) return;
    const newTodo = {
        id: Date.now().toString(),
        text,
        completed: false,
    };
    todos.push(newTodo);
    saveTodos();
    renderTodos();
    newTodoInput.value = '';
}

/**
 * Toggle the completion state of a todo by its id.
 * @param {string} id
 */
function toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    if (todo) {
        todo.completed = !todo.completed;
        saveTodos();
        renderTodos();
    }
}

/**
 * Delete a todo from the list by its id.
 * @param {string} id
 */
function deleteTodo(id) {
    todos = todos.filter(t => t.id !== id);
    saveTodos();
    renderTodos();
}

// Initialization
loadTodos();
renderTodos();
if (todoForm) {
    todoForm.addEventListener('submit', handleAddTodo);
}
