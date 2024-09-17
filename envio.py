import socket

def send_message(server_ip, server_port, message):
    # Crear un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectar al servidor
        client_socket.connect((server_ip, server_port))
        print(f"Conectado al servidor en {server_ip}:{server_port}")

        # Enviar mensaje
        client_socket.sendall(message.encode('utf-8'))
        print(f"Mensaje enviado: {message}")

    finally:
        # Cerrar el socket
        client_socket.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    # Reemplaza 'server_ip' con la IP de la máquina que está ejecutando el servidor
    #server_ip = '38.43.134.172'  # Reemplaza con la IP adecuada
    server_ip = 'localhost'
    server_port = 6061
    message = "Hola, este es un mensaje de prueba."
    datam = "863719063922554"
    send_message(server_ip, server_port, datam)
