from flask import Flask, render_template, request, redirect, session
from flask import session
from flask import Flask, render_template, request, redirect
import sqlite3
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'


def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
init_db()

@app.route('/')
def index():
    return redirect('/splash')

@app.route('/splash')
def splash():
    return render_template('splash.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not username or not password or not confirm:
            return "Preencha todos os campos"

        if password != confirm:
            return "As senhas não coincidem"

        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Usuário já existe"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Por favor, preencha todos os campos"

        with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

        if user and user[2] == password:  
            session['username'] = username
            return redirect('/homepage')
        else:
            return "Login inválido"

    return render_template('login.html')  


@app.route('/homepage')
def idea():
    if 'username' not in session:
        return redirect('/login')
    return render_template("homepage.html", username=session['username'])


@app.route('/novidades')
def novidades():
    return render_template("novidades.html")

@app.route('/coleções')
def colecoes():
    return render_template("colecoes.html")

@app.route('/drops')
def drops():
    return render_template("drops.html")

@app.route('/contato')
def contato():
    return render_template("contato.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
