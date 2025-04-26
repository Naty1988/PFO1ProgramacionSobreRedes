import sqlite3

def mostrar_mensajes():
    conn = sqlite3.connect("mensajes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM mensajes")
    mensajes = cursor.fetchall()

    for m in mensajes:
        print(f"ID: {m[0]} | Contenido: {m[1]} | Fecha: {m[2]} | IP: {m[3]}")

    conn.close()

if __name__ == "__main__":
    mostrar_mensajes()
