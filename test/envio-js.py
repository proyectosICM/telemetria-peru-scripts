import socket
import json

def send_message(server_ip, server_port, data):
    # Crear un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectar al servidor
        client_socket.connect((server_ip, server_port))
        print(f"Conectado al servidor en {server_ip}:{server_port}")

        # Convertir el diccionario a JSON y enviar el mensaje
        json_message = json.dumps(data)
        client_socket.sendall(json_message.encode('utf-8'))
        print(f"Mensaje JSON enviado: {json_message}")

    finally:
        # Cerrar el socket
        client_socket.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    # Reemplaza 'server_ip' con la IP de la máquina que está ejecutando el servidor
    server_ip = '38.43.134.172'  # Reemplaza con la IP adecuada
    server_port = 9525

    # Datos de prueba en formato JSON
    data = {
        "mensaje": "Hola, este es un mensaje de prueba.",
        "numero": 123,
        "activo": True
    }

    send_message(server_ip, server_port, data)
