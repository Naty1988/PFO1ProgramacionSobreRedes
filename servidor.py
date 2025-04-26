import socket
import sqlite3
from datetime import datetime
import threading

# Lista para mantener las conexiones de los clientes
clientes = []

def inicializar_db():
    try:
        conn = sqlite3.connect("mensajes.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo acceder a la base de datos: {e}")
        exit(1)

def inicializar_socket():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("127.0.0.1", 5000))  # Escuchar en localhost:5000
        server_socket.listen(5)  # Máximo 5 conexiones en cola
        print("[INFO] Servidor escuchando en 127.0.0.1:5000")
        return server_socket
    except socket.error as e:
        print(f"[ERROR] No se pudo iniciar el servidor: {e}")
        exit(1)

def guardar_mensaje(contenido, ip_cliente):
    try:
        conn = sqlite3.connect("mensajes.db")
        cursor = conn.cursor()
        fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        ''', (contenido, fecha_envio, ip_cliente))
        conn.commit()
        conn.close()
        return fecha_envio
    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo guardar el mensaje: {e}")
        return None

def manejar_cliente(cliente_socket, direccion):
    ip_cliente = direccion[0]
    print(f"[INFO] Conexión aceptada de {ip_cliente}")
    try:
        while True:
            mensaje = cliente_socket.recv(1024).decode("utf-8")
            if not mensaje:
                break
            print(f"[MENSAJE] Recibido de {ip_cliente}: {mensaje}")
            
            timestamp = guardar_mensaje(mensaje, ip_cliente)
            if timestamp:
                respuesta = f"Mensaje recibido: {timestamp}"
            else:
                respuesta = "Error al guardar el mensaje."
            cliente_socket.send(respuesta.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Conexión con {ip_cliente} fallida: {e}")
    finally:
        cliente_socket.close()
        print(f"[INFO] Conexión cerrada con {ip_cliente}")

def aceptar_conexiones(servidor_socket):
    while True:
        cliente_socket, direccion = servidor_socket.accept()
        clientes.append(cliente_socket)  # Añadir cliente a la lista
        # Crear un hilo para manejar a cada cliente de manera concurrente
        hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
        hilo.start()

def enviar_mensaje_a_clientes(mensaje):
    """ Enviar un mensaje a todos los clientes conectados """
    for cliente in clientes:
        try:
            cliente.send(mensaje.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] No se pudo enviar mensaje a un cliente: {e}")

def leer_mensajes_consola():
    """ Leer mensajes de la consola para enviar al cliente """
    while True:
        mensaje_servidor = input("[Servidor] Escribe un mensaje para enviar a todos los clientes: ")
        if mensaje_servidor.lower() == "salir":
            break
        # Enviar el mensaje a todos los clientes
        enviar_mensaje_a_clientes(mensaje_servidor)

if __name__ == "__main__":
    inicializar_db()
    servidor = inicializar_socket()

    # Iniciar un hilo para aceptar conexiones de clientes
    hilo_conexiones = threading.Thread(target=aceptar_conexiones, args=(servidor,))
    hilo_conexiones.start()

    # Iniciar lectura de mensajes desde la consola para enviar a los clientes
    leer_mensajes_consola()

