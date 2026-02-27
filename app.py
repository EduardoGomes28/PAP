from flask import Flask, render_template, request, redirect, session
import json
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'

STORE_DB = "loja.db"


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


def _row_to_product(row):
    return {
        "slug": row["slug"],
        "name": row["name"],
        "description": row["description"],
        "price": row["price"],
        "badge": row["badge"],
        "image": row["image"],
        "sizes": json.loads(row["sizes"]) if row["sizes"] else [],
        "in_stock": bool(row["in_stock"]),
    }


def init_products_db():
    with sqlite3.connect(STORE_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price TEXT NOT NULL,
                badge TEXT NOT NULL DEFAULT '',
                image TEXT NOT NULL,
                sizes TEXT NOT NULL,
                in_stock INTEGER NOT NULL DEFAULT 1
            )
            """
        )

def get_products_by_category(category):
    with sqlite3.connect(STORE_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT slug, name, description, price, badge, image, sizes, in_stock FROM products WHERE category = ? ORDER BY id",
            (category,),
        ).fetchall()
    return [_row_to_product(row) for row in rows]


def get_product_by_slug(slug):
    with sqlite3.connect(STORE_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT slug, name, description, price, badge, image, sizes, in_stock FROM products WHERE slug = ?",
            (slug,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_product(row)


init_products_db()

@app.route('/')
def index():
    return redirect('/intro')

@app.route('/intro')
def splash():
    return render_template('intro.html')


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
def homepage():
    if 'username' not in session:
        return redirect('/login')
    return render_template("homepage.html", username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/jackets')
def jackets():
    return render_template("js.html", products=get_products_by_category("jackets"))


@app.route('/produto/<slug>')
def produto_detalhe(slug):
    product = get_product_by_slug(slug)
    if product is None:
        return "Produto não encontrado", 404
    return render_template("produto.html", product=product)

@app.route('/shoes')
def shoes():
    return render_template("shoes.html", products=get_products_by_category("shoes"))

@app.route('/calcas')
def contato():
    return render_template("calças.html", products=get_products_by_category("pants"))


if __name__ == '__main__':
    app.run(debug=True)

 


