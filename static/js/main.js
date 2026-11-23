// ==== Канбан ====
async function loadKanban() {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    ['todo', 'doing', 'done'].forEach(col => {
        const el = document.getElementById('col-' + col);
        el.innerHTML = '';
        data[col].forEach(task => el.appendChild(renderTask(task, col)));
    });
}

function renderTask(task, column) {
    const div = document.createElement('div');
    div.className = 'task';
    div.dataset.priority = task.priority || 'medium';
    div.dataset.id = task.id;

    const span = document.createElement('span');
    span.textContent = task.text;

    const actions = document.createElement('div');
    actions.className = 'task-actions';

    if (column !== 'todo') {
        const left = document.createElement('button');
        left.textContent = '←';
        left.title = 'Влево';
        left.onclick = () => moveTask(task.id, column === 'done' ? 'doing' : 'todo');
        actions.appendChild(left);
    }
    if (column !== 'done') {
        const right = document.createElement('button');
        right.textContent = '→';
        right.title = 'Вправо';
        right.onclick = () => moveTask(task.id, column === 'todo' ? 'doing' : 'done');
        actions.appendChild(right);
    }
    const del = document.createElement('button');
    del.textContent = '✕';
    del.title = 'Удалить';
    del.onclick = () => deleteTask(task.id);
    actions.appendChild(del);

    div.appendChild(span);
    div.appendChild(actions);
    return div;
}

async function addTask() {
    const input = document.getElementById('task-text');
    const priority = document.getElementById('task-priority').value;
    const text = input.value.trim();
    if (!text) return;
    await fetch('/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, priority})
    });
    input.value = '';
    loadKanban();
}

async function moveTask(id, column) {
    await fetch('/api/tasks/' + id, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({column})
    });
    loadKanban();
}

async function deleteTask(id) {
    if (!confirm('Удалить задачу?')) return;
    await fetch('/api/tasks/' + id, {method: 'DELETE'});
    loadKanban();
}

if (document.getElementById('kanban')) {
    document.getElementById('add-btn').addEventListener('click', addTask);
    document.getElementById('task-text').addEventListener('keydown', e => {
        if (e.key === 'Enter') addTask();
    });
    loadKanban();
}

// ==== Таймер Pomodoro ====
if (document.getElementById('timer')) {
    const display = document.getElementById('timer');
    const status = document.getElementById('timer-status');
    const startBtn = document.getElementById('start-btn');
    const resetBtn = document.getElementById('reset-btn');
    let timeLeft = 25 * 60;
    let interval = null;
    let running = false;

    function update() {
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        display.textContent = `${m}:${s}`;
    }
    function tick() {
        timeLeft--;
        update();
        if (timeLeft <= 0) {
            clearInterval(interval);
            running = false;
            startBtn.textContent = 'Старт';
            status.textContent = '🍅 Отдохни 5 минут!';
            alert('Время вышло! Сделай перерыв.');
            timeLeft = 25 * 60;
            update();
        }
    }
    startBtn.addEventListener('click', () => {
        if (running) {
            clearInterval(interval);
            running = false;
            startBtn.textContent = 'Старт';
            status.textContent = 'Пауза';
        } else {
            interval = setInterval(tick, 1000);
            running = true;
            startBtn.textContent = 'Пауза';
            status.textContent = 'Работаем...';
        }
    });
    resetBtn.addEventListener('click', () => {
        clearInterval(interval);
        running = false;
        timeLeft = 25 * 60;
        update();
        startBtn.textContent = 'Старт';
        status.textContent = 'Готов к работе';
    });
    update();
}