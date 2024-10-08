import socket

def start_server(host='0.0.0.0', port=9525):
    # Crear un socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Vincular el socket a la dirección y el puerto
    server_socket.bind((host, port))

    # Escuchar conexiones entrantes
    server_socket.listen(1)
    print(f"Servidor escuchando en {host}:{port}")

    while True:
        # Esperar a que llegue una conexión
        client_socket, client_address = server_socket.accept()
        print(f"Conexión establecida con {client_address}")

        try:
            while True:
                # Recibir datos (tamaño del búfer = 1024 bytes)
                data = client_socket.recv(1024)
                if data:
                    print(f"Datos recibidos: {data.decode('utf-8')}")
                else:
                    # No hay más datos, cerrar la conexión
                    break
        finally:
            # Cerrar la conexión
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
