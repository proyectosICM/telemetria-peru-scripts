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
            # Buffer para acumular los datos
            buffer = b''

            # Recibir el IMEI en formato hexadecimal
            data = client_socket.recv(1024)
            if data:
                # Imprimir los datos recibidos en formato hexadecimal
                print(f"Datos recibidos: {data}")
                print(f"Datos recibidos (hex): {data.hex()}")

                # Extraer la longitud del IMEI (primeros 2 bytes)
                imei_length_hex = data[:2]  # Los primeros dos bytes son la longitud del IMEI
                imei_length = int(imei_length_hex.hex(), 16)  # Convertir de hexadecimal a decimal

                # Extraer los bytes que representan el IMEI
                imei_hex = data[2:2+imei_length]  # Los siguientes bytes son el IMEI
                imei = imei_hex.decode('ascii')  # Convertir los bytes a texto ASCII

                print(f"IMEI recibido: {imei}")

                # Validar el IMEI
                if len(imei) == 15 and imei.isdigit():
                    print("IMEI válido")
                    
                    # Enviar mensaje de confirmación si el IMEI es válido
                    confirmation_message = b'\x01'  # Mensaje de confirmación (01 en hexadecimal)
                    try:
                        client_socket.sendall(confirmation_message)
                        print("Mensaje de confirmación enviado correctamente")

                        # Esperar al menos dos mensajes antes de procesar
                        messages_received = 0
                        while messages_received < 2:
                            new_data = client_socket.recv(1024)
                            if new_data:
                                buffer += new_data  # Acumular datos en el buffer
                                buffer_size = len(buffer)  # Tamaño acumulado del buffer
                                messages_received += 1
                            else:
                                print("El dispositivo ha cerrado la conexión")
                                break

                        # Procesar y mostrar el buffer acumulado
                        # print(f"Datos Nativos acumulados en el buffer: {buffer}")
                        # print(f"Datos acumulados en el buffer: {buffer.hex()}")
                        # print(f"Tamaño final del buffer: {len(buffer)} bytes")
                        parsed_data = parse_codec8_extended(buffer)
                        if parsed_data:
                            # Incluir el IMEI en los resultados promedios
                            parsed_data['averages']['imei'] = imei
                            # Imprimir el JSON con los resultados promedios
                            print("Datos promedios:")
                            print(json.dumps(parsed_data['averages'], indent=4))
                            send_to_mqtt(parsed_data['averages'])

                    except Exception as e:
                        print(f"Error al enviar el mensaje de confirmación: {e}")
                else:
                    print("IMEI inválido")

            else:
                print("El dispositivo ha cerrado la conexión")

        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")
            print("*************************************")
