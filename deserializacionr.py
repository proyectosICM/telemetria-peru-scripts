import socket
import struct

def parse_codec8_extended(data):
    # Verifica si la longitud de los datos es suficiente
    if len(data) < 12:
        print("Datos incompletos")
        return None

    # Desempaqueta la cabecera y el campo de eventos
    try:
        preamble = data[:4]
        data_field_length = struct.unpack('!H', data[4:6])[0]
        codec_id = data[6]
        number_of_data = data[7]

        print(f"Preamble: 4 bytes, valor: {int.from_bytes(preamble, 'big')}, hex: {preamble.hex()}")
        print(f"AVL Data Length: 2 bytes, valor: {data_field_length}, hex: {data[4:6].hex()}")
        print(f"Codec ID: 1 byte, valor: {codec_id}, hex: {data[6]:02X}")
        print(f"AVL Data Count: 1 byte, valor: {number_of_data}, hex: {data[7]:02X}")
        
        offset = 8
        avl_data_list = []

        for i in range(number_of_data):
            if len(data) >= offset + 24:  # Asegura que haya suficientes datos para extraer un paquete AVL
                timestamp = struct.unpack('!Q', data[offset:offset+8])[0]
                priority = data[offset+8]

                print(f"Timestamp: 8 bytes, valor: {timestamp}, hex: {data[offset:offset+8].hex()}")
                print(f"Priority: 1 byte, valor: {priority}, hex: {data[offset+8]:02X}")

                longitude = struct.unpack('!i', data[offset+9:offset+13])[0]  # Longitud
                latitude = struct.unpack('!i', data[offset+13:offset+17])[0]  # Latitud
                altitude = struct.unpack('!H', data[offset+17:offset+19])[0]  # Altitud
                angle = struct.unpack('!H', data[offset+19:offset+21])[0]     # Ángulo
                satellites = data[offset+21]                                 # Número de satélites
                speed = struct.unpack('!H', data[offset+22:offset+24])[0]    # Velocidad

                print(f"Longitude: 4 bytes, valor: {longitude}, hex: {data[offset+9:offset+13].hex()}")
                print(f"Latitude: 4 bytes, valor: {latitude}, hex: {data[offset+13:offset+17].hex()}")
                print(f"Altitude: 2 bytes, valor: {altitude}, hex: {data[offset+17:offset+19].hex()}")
                print(f"Angle: 2 bytes, valor: {angle}, hex: {data[offset+19:offset+21].hex()}")
                print(f"Satellites: 1 byte, valor: {satellites}, hex: {data[offset+21]:02X}")
                print(f"Speed: 2 bytes, valor: {speed}, hex: {data[offset+22:offset+24].hex()}")

                offset += 24

                # Número de elementos IO
                event_id = data[offset]
                total_io_elements = data[offset+1]
                offset += 2

                print(f"Event ID: 1 byte, valor: {event_id}, hex: {event_id:02X}")
                print(f"Total IO Elements: 1 byte, valor: {total_io_elements}, hex: {total_io_elements:02X}")

                io_elements = {}

                # Lectura de IO elements
                io_elements['1B'] = {}
                io_count_1B = data[offset]
                offset += 1
                print(f"IO Count (1B): 1 byte, valor: {io_count_1B}, hex: {io_count_1B:02X}")

                for _ in range(io_count_1B):
                    io_id = data[offset]
                    io_value = data[offset+1]
                    io_elements['1B'][io_id] = io_value
                    print(f"IO Element (1B): ID: {io_id:02X}, valor: {io_value}, hex: {io_value:02X}")
                    offset += 2

                io_elements['2B'] = {}
                io_count_2B = data[offset]
                offset += 1
                print(f"IO Count (2B): 1 byte, valor: {io_count_2B}, hex: {io_count_2B:02X}")

                for _ in range(io_count_2B):
                    io_id = data[offset]
                    io_value = struct.unpack('!H', data[offset+1:offset+3])[0]
                    io_elements['2B'][io_id] = io_value
                    print(f"IO Element (2B): ID: {io_id:02X}, valor: {io_value}, hex: {data[offset+1:offset+3].hex()}")
                    offset += 3

                io_elements['4B'] = {}
                io_count_4B = data[offset]
                offset += 1
                print(f"IO Count (4B): 1 byte, valor: {io_count_4B}, hex: {io_count_4B:02X}")

                for _ in range(io_count_4B):
                    io_id = data[offset]
                    io_value = struct.unpack('!I', data[offset+1:offset+5])[0]
                    io_elements['4B'][io_id] = io_value
                    print(f"IO Element (4B): ID: {io_id:02X}, valor: {io_value}, hex: {data[offset+1:offset+5].hex()}")
                    offset += 5

                io_elements['8B'] = {}
                io_count_8B = data[offset]
                offset += 1
                print(f"IO Count (8B): 1 byte, valor: {io_count_8B}, hex: {io_count_8B:02X}")

                for _ in range(io_count_8B):
                    io_id = data[offset]
                    io_value = struct.unpack('!Q', data[offset+1:offset+9])[0]
                    io_elements['8B'][io_id] = io_value
                    print(f"IO Element (8B): ID: {io_id:02X}, valor: {io_value}, hex: {data[offset+1:offset+9].hex()}")
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

        crc = struct.unpack('!I', data[-4:])[0]  # CRC
        print(f"CRC: 4 bytes, valor: {crc}, hex: {data[-4:].hex()}")

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
            # Enviar confirmación de conexión
            confirmation_message = b'\x01'  # Mensaje de confirmación (01 en hexadecimal)
            try:
                bytes_sent = client_socket.sendall(confirmation_message)
                if bytes_sent is None:
                    print("Mensaje de confirmación enviado correctamente")
                else:
                    print(f"Mensaje de confirmación enviado, bytes enviados: {bytes_sent}")
            except Exception as e:
                print(f"Error al enviar el mensaje de confirmación: {e}")

            while True:
                data = client_socket.recv(1024)
                if data:
                    # Imprime los datos recibidos en formato hexadecimal
                    print(f"Datos recibidos: {data}")
                    print(f"Datos recibidos (hex): {data.hex()}")

                    # Intentar deserializar los datos
                    codec8_data = parse_codec8_extended(data)
                    if codec8_data:
                        print(f"Datos Codec 8 extendido deserializados: {codec8_data}")
                else:
                    print("El dispositivo ha cerrado la conexión")
                    break
        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

if __name__ == "__main__":
    start_server()
