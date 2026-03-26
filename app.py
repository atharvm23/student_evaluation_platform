from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Create Database
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task TEXT,
                    status INTEGER)''')

    conn.commit()
    conn.close()

init_db()

# Home → Login
@app.route('/')
def home():
    return render_template("login.html")

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template("register.html")

# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')
    else:
        return "Invalid Login"

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Add Task
    if request.method == "POST":
        task = request.form['task']
        c.execute("INSERT INTO tasks (user_id, task, status) VALUES (?, ?, 0)", (user_id, task))
        conn.commit()

    # Fetch Tasks
    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()

    # Calculate Score
    total = len(tasks)
    completed = sum(1 for t in tasks if t[3] == 1)
    score = (completed / total * 100) if total > 0 else 0

    conn.close()

    return render_template("dashboard.html", tasks=tasks, score=score)

# Mark Done
@app.route('/done/<int:id>')
def done(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET status=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Run App
if __name__ == "__main__":
    app.run(debug=True)