import socket
from parse_codec8_extended import parse_codec8_extended
from mqtt_manager import send_to_mqtt
import json

def start_server(host='0.0.0.0', port=9525):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Servidor escuchando en {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión establecida con {client_address}")

        try:
            buffer = b''
            data = client_socket.recv(1024)
            if data:
                print(f"Datos recibidos (hex): {data.hex()}")

                imei_length_hex = data[:2]
                imei_length = int(imei_length_hex.hex(), 16)
                imei_hex = data[2:2+imei_length]
                imei = imei_hex.decode('ascii')

                if len(imei) == 15 and imei.isdigit():
                    confirmation_message = b'\x01'
                    client_socket.sendall(confirmation_message)
                    print("Mensaje de confirmación enviado correctamente")

                    buffer += client_socket.recv(1024)
                    parsed_data = parse_codec8_extended(buffer)
                    if parsed_data:
                        parsed_data['averages']['imei'] = imei
                        send_to_mqtt(parsed_data['averages'])
            else:
                print("El dispositivo ha cerrado la conexión")

        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")
