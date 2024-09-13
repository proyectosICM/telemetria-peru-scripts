import socket
import struct

def start_server(host='0.0.0.0', port=9525):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)
    print(f"Servidor escuchando en {host}:{port}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión establecida con {client_address}")
              
        try:
            # Leer IMEI
            imei_length_data = client_socket.recv(2)
            imei_length = struct.unpack('!H', imei_length_data)[0]
            imei_data = client_socket.recv(imei_length)
            imei = imei_data.decode('ascii')
            print(f"IMEI recibido: {imei}")
            
            # Validar IMEI
            imei_valid = True  # Cambiar según la lógica de validación
            confirmation_message = b'\x01' if imei_valid else b'\x00'
            client_socket.sendall(confirmation_message)
            print(f"Mensaje de confirmación de IMEI enviado: {confirmation_message.hex()}")

            if not imei_valid:
                print("IMEI no válido, cerrando conexión")
                continue
            
            while True: 
                data = client_socket.recv(1024)
        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
