import socket

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

                        # Continuar esperando nuevos mensajes después de la confirmación
                        while True:
                            new_data = client_socket.recv(1024)
                            if new_data:
                                buffer += new_data  # Acumular datos en el buffer
                                print(f"Nuevos datos recibidos (hex): {buffer.hex()}")
                            else:
                                print("El dispositivo ha cerrado la conexión")
                                break

                    except Exception as e:
                        print(f"Error al enviar el mensaje de confirmación: {e}")
                else:
                    print("IMEI inválido")

            else:
                print("El dispositivo ha cerrado la conexión")

        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
