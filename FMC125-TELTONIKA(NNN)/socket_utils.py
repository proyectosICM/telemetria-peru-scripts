import socket
import multiprocessing
from codec8_extended_parser import parse_codec8_extended
from config import HOST, PORT
from socket_sender import send_to_socket

def send_confirmation_message(client_socket):
    confirmation_message = b'\x01'
    try:
        client_socket.sendall(confirmation_message)
        print("Mensaje de confirmación enviado correctamente")
    except Exception as e:
        print(f"Error al enviar el mensaje de confirmación: {e}")
        
def process_data(data):
    codec8_data = parse_codec8_extended(data)
    if codec8_data:
        print(f"Datos Codec 8 extendido deserializados: {codec8_data}")
        serialized_data = str(codec8_data).encode('utf-8')
        send_to_socket(serialized_data)

def handle_client(client_socket):
    with client_socket:
        send_confirmation_message(client_socket)

        while True:
            data = client_socket.recv(1024)
            if data:
                print(f"Datos recibidos: {data}")
                print(f"Datos recibidos (hex): {data.hex()}")

                # Enviar los datos al proceso de procesamiento de datos
                process_data(data)
            else:
                print("El dispositivo ha cerrado la conexión")
                break

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Aumentar el número de conexiones en espera si es necesario
    print(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión establecida con {client_address}")

        # Crear un nuevo proceso para manejar el cliente
        client_process = multiprocessing.Process(target=handle_client, args=(client_socket,))
        client_process.start()
