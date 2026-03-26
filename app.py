from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table (with role)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    role TEXT)''')

    # Tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task TEXT,
                    status INTEGER)''')

    conn.commit()
    conn.close()

init_db()

# -------------------- HOME --------------------
@app.route('/')
def home():
    return render_template("login.html")

# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']   # NEW

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, password, role))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("register.html")

# -------------------- LOGIN --------------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, password))

    user = c.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['role'] = user[3]   # NEW

        # Role-based redirect
        if user[3] == "guardian":
            return redirect('/guardian')
        else:
            return redirect('/dashboard')
    else:
        return "Invalid Login"

# -------------------- STUDENT DASHBOARD --------------------
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
        c.execute("INSERT INTO tasks (user_id, task, status) VALUES (?, ?, 0)",
                  (user_id, task))
        conn.commit()

    # Fetch Tasks
    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()

    # Calculate Score (UPDATED for charts)
    completed = sum(1 for t in tasks if t[3] == 1)
    total = len(tasks)
    score = (completed / total * 100) if total > 0 else 0

    # Fetch username
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    username = user[0] if user else "Unknown"

    conn.close()

    return render_template("dashboard.html",
                           tasks=tasks,
                           score=score,
                           completed=completed,
                           total=total,
                           username=username)

# -------------------- MARK TASK DONE --------------------
@app.route('/done/<int:id>')
def done(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("UPDATE tasks SET status=1 WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -------------------- GUARDIAN DASHBOARD --------------------
@app.route('/guardian')
def guardian():
    if 'role' not in session or session['role'] != "guardian":
        return redirect('/')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # View ALL student tasks
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()

    completed = sum(1 for t in tasks if t[3] == 1)
    total = len(tasks)
    score = (completed / total * 100) if total > 0 else 0

    conn.close()

    return render_template("guardian.html",
                           tasks=tasks,
                           score=score)

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=True)