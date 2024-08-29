import socket
from config import HOST, API_PORT  # Importamos API_PORT desde la configuración

def send_to_socket(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, API_PORT))  # Usamos API_PORT directamente
            s.sendall(data)
            print(f"Datos enviados al socket en {HOST}:{API_PORT}")
    except Exception as e:
        print(f"Error al enviar los datos al socket en {HOST}:{API_PORT}: {e}")
