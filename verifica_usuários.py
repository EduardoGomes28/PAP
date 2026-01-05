import sqlite3

def mostrar_usuarios():
    with sqlite3.connect("users.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users")
        usuarios = cur.fetchall()
        if usuarios:
            print("Usuários cadastrados:")
            for u in usuarios:
                print(f"ID: {u[0]}, Usuário: {u[1]}, Senha: {u[2]}")
        else:
            print("Nenhum usuário encontrado.")

if __name__ == "__main__":
    mostrar_usuarios()
