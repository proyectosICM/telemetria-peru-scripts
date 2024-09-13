import socket
import struct

def parse_codec8_extended(data):
    if len(data) < 12:
        print("Datos incompletos")
        return None

    try:
        preamble = data[:4]
        data_field_length = struct.unpack('!H', data[4:6])[0]
        codec_id = data[6]
        number_of_data = data[7]
        
        offset = 8
        avl_data_list = []

        for _ in range(number_of_data):
            if len(data) >= offset + 24:
                timestamp = struct.unpack('!Q', data[offset:offset+8])[0]
                priority = data[offset+8]
                longitude = struct.unpack('!i', data[offset+9:offset+13])[0]
                latitude = struct.unpack('!i', data[offset+13:offset+17])[0]
                altitude = struct.unpack('!H', data[offset+17:offset+19])[0]
                angle = struct.unpack('!H', data[offset+19:offset+21])[0]
                satellites = data[offset+21]
                speed = struct.unpack('!H', data[offset+22:offset+24])[0]

                offset += 24

                event_id = data[offset]
                total_io_elements = data[offset+1]
                offset += 2

                io_elements = {'1B': {}, '2B': {}, '4B': {}, '8B': {}}

                # Read IO elements
                io_count_1B = data[offset]
                offset += 1
                for _ in range(io_count_1B):
                    io_id = data[offset]
                    io_value = data[offset+1]
                    io_elements['1B'][io_id] = io_value
                    offset += 2

                io_count_2B = data[offset]
                offset += 1
                for _ in range(io_count_2B):
                    io_id = data[offset]
                    io_value = struct.unpack('!H', data[offset+1:offset+3])[0]
                    io_elements['2B'][io_id] = io_value
                    offset += 3

                io_count_4B = data[offset]
                offset += 1
                for _ in range(io_count_4B):
                    io_id = data[offset]
                    io_value = struct.unpack('!I', data[offset+1:offset+5])[0]
                    io_elements['4B'][io_id] = io_value
                    offset += 5

                io_count_8B = data[offset]
                offset += 1
                for _ in range(io_count_8B):
                    io_id = data[offset]
                    io_value = struct.unpack('!Q', data[offset+1:offset+9])[0]
                    io_elements['8B'][io_id] = io_value
                    offset += 9

                avl_data_list.append({
                    "timestamp": timestamp,
                    "priority": priority,
                    "longitude": longitude,
                    "latitude": latitude,
                    "altitude": altitude,
                    "angle": angle,
                    "satellites": satellites,
                    "speed": speed,
                    "event_id": event_id,
                    "total_io_elements": total_io_elements,
                    "io_elements": io_elements
                })

            else:
                print("Datos insuficientes para extraer un AVL Data Packet completo")
                return None

        crc = struct.unpack('!I', data[-4:])[0]

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": crc
        }
    except struct.error as e:
        print(f"Error al deserializar los datos: {e}")
        return None

def start_server(host='0.0.0.0', port=9525):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
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

            # Validar IMEI (aquí deberías agregar la lógica real para validar)
            imei_valid = True  # Cambiar según la lógica de validación
            confirmation_message = b'\x01' if imei_valid else b'\x00'
            client_socket.sendall(confirmation_message)

            if not imei_valid:
                print("IMEI no válido, cerrando conexión")
                continue

            while True:
                data = client_socket.recv(1024)
                if data:
                    print(f"Datos recibidos: {data}")
                    print(f"Datos recibidos (hex): {data.hex()}")

                    codec8_data = parse_codec8_extended(data)
                    if codec8_data:
                        print(f"Datos Codec 8 extendido deserializados: {codec8_data}")

                        # Confirmar recepción de datos
                        num_data_received = len(codec8_data['avl_data_list'])
                        confirmation_data = struct.pack('!I', num_data_received)
                        client_socket.sendall(confirmation_data)

                else:
                    print("El dispositivo ha cerrado la conexión")
                    break
        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
