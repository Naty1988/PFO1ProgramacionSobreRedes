import socket

def cliente():
    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect(("127.0.0.1", 5000))  # Conectar con el servidor
        print("[INFO] Conectado al servidor.")
    except socket.error as e:
        print(f"[ERROR] No se pudo conectar al servidor: {e}")
        return

    try:
        while True:
            mensaje = input("Escribí un mensaje (o 'éxito' para salir): ")
            if mensaje.lower() == "éxito":
                print("[INFO] Cerrando conexión.")
                break

            cliente_socket.send(mensaje.encode("utf-8"))
            respuesta = cliente_socket.recv(1024).decode("utf-8")
            print("Servidor:", respuesta)
    except Exception as e:
        print(f"[ERROR] Fallo al enviar mensaje: {e}")
    finally:
        cliente_socket.close()

if __name__ == "__main__":
    cliente()
