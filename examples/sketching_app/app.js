// SketchPad core logic
// Implements canvas drawing, tools, undo/redo, and UI bindings.

(function () {
    // ----- DOM References -----
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    const toolbar = document.getElementById('toolbar');

    const colorSwatches = document.querySelectorAll('.color-swatch');
    const customColorPicker = document.getElementById('customColorPicker');
    const penSizeSlider = document.getElementById('penSize');
    const penSizeLabel = document.getElementById('penSizeLabel');
    const penBtn = document.getElementById('penBtn');
    const eraserBtn = document.getElementById('eraserBtn');
    const clearBtn = document.getElementById('clearBtn');
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    // ----- State -----
    const state = {
        currentTool: 'pen', // 'pen' | 'eraser'
        penColor: '#000000',
        penSize: 5,
        isDrawing: false,
        undoStack: [],
        redoStack: [],
        maxStackSize: 20,
    };

    // ----- Canvas Context Defaults -----
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = state.penColor;
    ctx.lineWidth = state.penSize;

    // ----- Utility Functions -----
    function getCanvasCoordinates(event) {
        const rect = canvas.getBoundingClientRect();
        // support pointer, mouse, touch events
        const clientX = event.clientX !== undefined ? event.clientX : (event.touches ? event.touches[0].clientX : 0);
        const clientY = event.clientY !== undefined ? event.clientY : (event.touches ? event.touches[0].clientY : 0);
        return {
            x: clientX - rect.left,
            y: clientY - rect.top,
        };
    }

    // Resize canvas to fill its container while preserving drawing
    function initCanvasSize() {
        // Preserve current drawing
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        tempCtx.drawImage(canvas, 0, 0);

        // Compute new size based on CSS layout (client width/height)
        const rect = canvas.getBoundingClientRect();
        const newWidth = Math.round(rect.width);
        const newHeight = Math.round(rect.height);
        if (newWidth > 0 && newHeight > 0) {
            canvas.width = newWidth;
            canvas.height = newHeight;
        }
        // Redraw preserved image scaled to new dimensions
        ctx.drawImage(tempCanvas, 0, 0, newWidth, newHeight);

        // Reapply context defaults (they are reset after size change)
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = state.penColor;
        ctx.lineWidth = state.penSize;
    }

    // ----- Tool Switching -----
    function setTool(toolName) {
        state.currentTool = toolName;
        // UI active class handling
        penBtn.classList.toggle('active', toolName === 'pen');
        eraserBtn.classList.toggle('active', toolName === 'eraser');
    }

    function updatePenColor(color) {
        state.penColor = color;
        // Update UI selection for swatches
        colorSwatches.forEach(swatch => {
            swatch.classList.toggle('selected', swatch.dataset.color.toLowerCase() === color.toLowerCase());
        });
        // Update custom picker value if it differs
        if (customColorPicker.value.toLowerCase() !== color.toLowerCase()) {
            customColorPicker.value = color;
        }
        // If current tool is pen, reflect immediately
        if (state.currentTool === 'pen') {
            ctx.strokeStyle = state.penColor;
        }
    }

    function updatePenSize(size) {
        const sz = Number(size);
        state.penSize = sz;
        penSizeLabel.textContent = sz;
        ctx.lineWidth = sz;
    }

    // ----- Undo / Redo -----
    function pushToUndoStack() {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        if (state.undoStack.length >= state.maxStackSize) {
            state.undoStack.shift();
        }
        state.undoStack.push(imageData);
        // Clear redo stack on new action
        state.redoStack = [];
    }

    function undo() {
        if (state.undoStack.length === 0) return;
        const current = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const previous = state.undoStack.pop();
        // push current to redo stack
        if (state.redoStack.length >= state.maxStackSize) {
            state.redoStack.shift();
        }
        state.redoStack.push(current);
        ctx.putImageData(previous, 0, 0);
    }

    function redo() {
        if (state.redoStack.length === 0) return;
        const current = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const next = state.redoStack.pop();
        if (state.undoStack.length >= state.maxStackSize) {
            state.undoStack.shift();
        }
        state.undoStack.push(current);
        ctx.putImageData(next, 0, 0);
    }

    // ----- Canvas Operations -----
    function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        state.undoStack = [];
        state.redoStack = [];
    }

    function downloadCanvas() {
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = 'sketchpad.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // ----- Drawing Event Handlers -----
    function handlePointerDown(e) {
        e.preventDefault();
        const { x, y } = getCanvasCoordinates(e);
        state.isDrawing = true;
        ctx.beginPath();
        ctx.moveTo(x, y);
        pushToUndoStack();
    }

    function handlePointerMove(e) {
        if (!state.isDrawing) return;
        e.preventDefault();
        const { x, y } = getCanvasCoordinates(e);
        // Set tool-specific styles
        if (state.currentTool === 'eraser') {
            ctx.globalCompositeOperation = 'destination-out';
            ctx.strokeStyle = 'rgba(0,0,0,1)'; // color doesn't matter when erasing
        } else {
            ctx.globalCompositeOperation = 'source-over';
            ctx.strokeStyle = state.penColor;
        }
        ctx.lineWidth = state.penSize;
        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    function handlePointerUp(e) {
        if (!state.isDrawing) return;
        e.preventDefault();
        ctx.closePath();
        state.isDrawing = false;
        // Reset composite operation for future pen strokes
        ctx.globalCompositeOperation = 'source-over';
    }

    // ----- UI Bindings -----
    function bindUI() {
        // Color swatches
        colorSwatches.forEach(swatch => {
            swatch.addEventListener('click', () => {
                const col = swatch.dataset.color;
                updatePenColor(col);
            });
        });
        // Custom color picker
        customColorPicker.addEventListener('input', (e) => {
            updatePenColor(e.target.value);
        });
        // Pen size slider
        penSizeSlider.addEventListener('input', (e) => {
            updatePenSize(e.target.value);
        });
        // Tool buttons
        penBtn.addEventListener('click', () => setTool('pen'));
        eraserBtn.addEventListener('click', () => setTool('eraser'));
        clearBtn.addEventListener('click', clearCanvas);
        undoBtn.addEventListener('click', undo);
        redoBtn.addEventListener('click', redo);
        downloadBtn.addEventListener('click', downloadCanvas);

        // Canvas drawing events – use pointer events with fallback to mouse/touch
        canvas.addEventListener('pointerdown', handlePointerDown);
        canvas.addEventListener('pointermove', handlePointerMove);
        canvas.addEventListener('pointerup', handlePointerUp);
        canvas.addEventListener('pointerleave', handlePointerUp);
        // Fallback for older browsers (optional)
        canvas.addEventListener('mousedown', handlePointerDown);
        canvas.addEventListener('mousemove', handlePointerMove);
        canvas.addEventListener('mouseup', handlePointerUp);
        canvas.addEventListener('mouseleave', handlePointerUp);
        canvas.addEventListener('touchstart', handlePointerDown, { passive: false });
        canvas.addEventListener('touchmove', handlePointerMove, { passive: false });
        canvas.addEventListener('touchend', handlePointerUp);
    }

    // ----- Responsive Resize -----
    window.addEventListener('resize', initCanvasSize);

    // ----- Initialization -----
    document.addEventListener('DOMContentLoaded', () => {
        // Initial UI state
        setTool(state.currentTool);
        updatePenColor(state.penColor);
        updatePenSize(state.penSize);
        bindUI();
        initCanvasSize();
    });

    // Expose for external use if needed
    window.SketchPad = {
        init: initCanvasSize,
    };
})();
