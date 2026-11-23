from flask import Flask, render_template, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"todo": [], "doing": [], "done": []}

def save_tasks(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Данные уроков (просто в коде, можно потом в БД)
LESSONS = [
    {
        "id": "intro",
        "title": "Введение в Python",
        "level": "Новичок",
        "duration": "15 мин",
        "content": """<h3>Что такое Python?</h3>
<p>Python — это язык программирования, который отлично подходит для начала обучения.
Он читается почти как английский текст.</p>
<pre><code>print("Привет, мир!")</code></pre>
<p>Попробуйте вывести своё имя:</p>
<pre><code>name = "Алекс"
print(f"Привет, {name}!")</code></pre>"""
    },
    {
        "id": "vars",
        "title": "Переменные и типы данных",
        "level": "Новичок",
        "duration": "20 мин",
        "content": """<h3>Переменные</h3>
<p>Переменная — это коробка, в которой хранится значение.</p>
<pre><code>age = 25          # int
name = "Иван"     # str
height = 1.82     # float
is_student = True # bool</code></pre>
<p>Пример: подсчёт времени на задачи.</p>
<pre><code>tasks = 5
hours_per_task = 1.5
total = tasks * hours_per_task
print(f"Всего нужно {total} часов")</code></pre>"""
    },
    {
        "id": "loops",
        "title": "Циклы и списки",
        "level": "Средний",
        "duration": "25 мин",
        "content": """<h3>Списки и циклы</h3>
<p>Список хранит несколько значений. Цикл позволяет пройти по ним.</p>
<pre><code>tasks = ["учёба", "спорт", "чтение"]
for task in tasks:
    print(f"Делаю: {task}")</code></pre>
<h3>Цикл while — для таймера</h3>
<pre><code>minutes = 25
while minutes > 0:
    print(f"Осталось {minutes} мин")
    minutes -= 5</code></pre>"""
    },
    {
        "id": "functions",
        "title": "Функции",
        "level": "Средний",
        "duration": "20 мин",
        "content": """<h3>Функции</h3>
<p>Функция — это блок кода, который можно вызвать много раз.</p>
<pre><code>def pomodoro(minutes):
    return f"Работай {minutes} минут, потом отдохни 5"

print(pomodoro(25))</code></pre>
<p>Функция для оценки загрузки дня:</p>
<pre><code>def load_level(hours):
    if hours > 8:
        return "Перегруз!"
    elif hours > 6:
        return "Плотно"
    return "Норм"

print(load_level(7))</code></pre>"""
    },
]

@app.route("/")
def index():
    return render_template("index.html", lessons=LESSONS[:3])

@app.route("/lessons")
def lessons():
    return render_template("lessons.html", lessons=LESSONS)

@app.route("/lessons/<lesson_id>")
def lesson(lesson_id):
    lesson = next((l for l in LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        return "Урок не найден", 404
    return render_template("lesson.html", lesson=lesson)

@app.route("/kanban")
def kanban():
    return render_template("kanban.html")

@app.route("/timer")
def timer():
    return render_template("timer.html")

@app.route("/about")
def about():
    return render_template("about.html")

# === API для канбана ===
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = load_tasks()
    payload = request.get_json()
    task = {
        "id": str(datetime.now().timestamp()),
        "text": payload.get("text", ""),
        "priority": payload.get("priority", "medium"),
    }
    data["todo"].append(task)
    save_tasks(data)
    return jsonify(task), 201

@app.route("/api/tasks/<task_id>", methods=["PUT"])
def move_task(task_id):
    data = load_tasks()
    payload = request.get_json()
    new_col = payload.get("column")
    for col in data:
        for i, t in enumerate(data[col]):
            if t["id"] == task_id:
                task = data[col].pop(i)
                data[new_col].append(task)
                save_tasks(data)
                return jsonify(task)
    return "Task not found", 404

@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    data = load_tasks()
    for col in data:
        data[col] = [t for t in data[col] if t["id"] != task_id]
    save_tasks(data)
    return "", 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)