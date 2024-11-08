import socket

def start_server(host='0.0.0.0', port=9526):
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
            # Fase inicial: verificar el IMEI y enviar confirmación si es válido
            data = client_socket.recv(1024)
            if data:
                imei_length_hex = data[:2]
                imei_length = int(imei_length_hex.hex(), 16)
                imei_hex = data[2:2 + imei_length]
                imei = imei_hex.decode('ascii')

                if len(imei) == 15 and imei.isdigit():
                    print(f"IMEI recibido y válido: {imei}")

                    # Enviar mensaje de confirmación
                    confirmation_message = b'\x01'
                    client_socket.sendall(confirmation_message)

                    # Segunda fase: recibir y procesar más mensajes
                    buffer = b''
                    while True:
                        new_data = client_socket.recv(1024)
                        if new_data:
                            buffer += new_data
                            print(f"Datos recibidos (hex): {new_data.hex()}")
                        else:
                            # El cliente se ha desconectado
                            print(f"Cliente {client_address} desconectado.")
                            break

                    # Aquí puedes procesar el buffer completo como sea necesario
                    hex_str = buffer.hex()
                    print(f"Buffer acumulado: {hex_str}")
                else:
                    print("IMEI inválido, cerrando conexión.")

            else:
                print("El dispositivo ha cerrado la conexión sin enviar datos.")

        finally:
            # Cerrar la conexión
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
