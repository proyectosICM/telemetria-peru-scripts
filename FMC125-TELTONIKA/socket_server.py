import socket
from parse_codec8_extended import parse_codec8_extended
from mqtt_manager import send_to_mqtt
import json
from threading import Event
import struct 

# Optional debugging lines: Uncomment lines 24, 45, 46, 53, 56, 67, 72, 83, and 84
# to view additional output in the console and help trace execution.

def start_server(stop_event, host='0.0.0.0', port=9526):
    # Create the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configuración adicional para evitar errores de "Address already in use"
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización del puerto
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))  # Liberar puerto inmediatamente
    
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")
    
    # Set a timeout to check the stop signal
    server_socket.settimeout(1)  
    try: 
        while not stop_event.is_set():
            try:
                try:
                    client_socket, client_address = server_socket.accept()
                    # print(f"Connection established with {client_address}")

                    # Start processing client data
                    handle_client(client_socket, client_address)

                except socket.timeout:
                    # Continue on timeout, allowing the loop to run as long as the server is not stopped
                    continue
            except Exception as e:
                print(f"Server error: {e}")
    finally:
        # Cerrar el socket del servidor cuando se detiene
        server_socket.close()
        print("Server stopped.")
    # Close the server socket when stopped
    server_socket.close()
    print("Server stopped.")

def handle_client(client_socket, client_address):
    try:
        buffer = b''
        data = client_socket.recv(1024)

        if data:
            # print(f"Data received: {data}")
            # print(f"Data received (hex): {data.hex()}")
            imei_length_hex = data[:2]
            imei_length = int(imei_length_hex.hex(), 16)
            imei_hex = data[2:2+imei_length]
            imei = imei_hex.decode('ascii')

            # print(f"IMEI received: {imei}")

            if len(imei) == 15 and imei.isdigit():
                # print("Valid IMEI")
                confirmation_message = b'\x01'
                client_socket.sendall(confirmation_message)

                messages_received = 0
                while messages_received < 2:
                    new_data = client_socket.recv(1024)
                    if new_data:
                        buffer += new_data
                        messages_received += 1
                    else:
                        # print("The device has closed the connection")
                        break
                
                # print(f"Buffer:  {buffer}")
                # hex_str = buffer.hex()
                # print(hex_str)    
                parsed_data = parse_codec8_extended(buffer, imei)
                if parsed_data:
                    # print(json.dumps(parsed_data['averages'], indent=4))
                    send_to_mqtt(parsed_data['data'])
                    buffer = b''
                    data = b''
            else:
                print("Invalid IMEI")

        else:
            print("The device has closed the connection")

    finally:
        client_socket.close()
        # print(f"Connection closed with {client_address}")
        # print("*************************************")
