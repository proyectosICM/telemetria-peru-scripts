import socket
from parse_codec8_extended import parse_codec8_extended
from mqtt_manager import send_to_mqtt
import json
from threading import Event

# Lineas a descomentar para debug
# 24, 45, 46, 53, 56, 67, 72, 83, 84

def start_server(stop_event, host='0.0.0.0', port=9525):
    # Crear el socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Servidor escuchando en {host}:{port}")
    
    # Establecer un timeout para verificar la señal de detener
    server_socket.settimeout(1)  

    while not stop_event.is_set():
        try:
            try:
                client_socket, client_address = server_socket.accept()
                #print(f"Conexión establecida con {client_address}")

                # Iniciar el procesamiento de datos del cliente
                handle_client(client_socket, client_address)

            except socket.timeout:
                # Continuar en caso de timeout, permitiendo que el bucle se ejecute mientras no se detenga el servidor
                continue
        except Exception as e:
            print(f"Error en el servidor: {e}")
    
    # Cerrar el socket del servidor cuando se detenga
    server_socket.close()
    print("Servidor detenido.")

def handle_client(client_socket, client_address):
    try:
        buffer = b''
        data = client_socket.recv(1024)

        if data:
            #print(f"Datos recibidos: {data}")
            #print(f"Datos recibidos (hex): {data.hex()}")

            imei_length_hex = data[:2]
            imei_length = int(imei_length_hex.hex(), 16)
            imei_hex = data[2:2+imei_length]
            imei = imei_hex.decode('ascii')

            # print(f"IMEI recibido: {imei}")

            if len(imei) == 15 and imei.isdigit():
                # print("IMEI válido")
                confirmation_message = b'\x01'
                client_socket.sendall(confirmation_message)

                messages_received = 0
                while messages_received < 2:
                    new_data = client_socket.recv(1024)
                    if new_data:
                        buffer += new_data
                        messages_received += 1
                    else:
                        # print("El dispositivo ha cerrado la conexión")
                        break
                
                print(f"Buffer:  {buffer}")
                parsed_data = parse_codec8_extended(buffer, imei)
                if parsed_data:
                    print(json.dumps(parsed_data['averages'], indent=4))
                    send_to_mqtt(parsed_data['averages'])

            else:
                print("IMEI inválido")

        else:
            print("El dispositivo ha cerrado la conexión")

    finally:
        client_socket.close()
        # print(f"Conexión cerrada con {client_address}")
        # print("*************************************")
