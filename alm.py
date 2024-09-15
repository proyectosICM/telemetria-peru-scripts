import socket
import struct

def hex_to_bytes(hex_str):
    """Convierte una cadena hexadecimal en datos binarios."""
    return bytes.fromhex(hex_str)

def parse_codec8_extended(data):
    # Convierte los datos de hexadecimal a binario si es necesario
    if isinstance(data, str):
        data = hex_to_bytes(data)

    if len(data) < 12:
        print("Datos incompletos")
        return None

    try:
        preamble = data[:4]
        print(f"Preamble: {preamble.hex()}")

        data_field_length = struct.unpack('!I', data[4:8])[0]
        print(f"Data Field Length: {data_field_length}")

        codec_id = data[8]
        print(f"Codec ID: {codec_id}")

        number_of_data = data[9]
        print(f"Number of Data: {number_of_data}")

        offset = 10
        avl_data_list = []

        for i in range(number_of_data):
            print(f"\nProcesando AVL Data Packet {i+1}/{number_of_data}...")

            if len(data) < offset + 24:  # Verifica si hay suficiente data para el paquete
                print(f"Datos insuficientes para extraer un AVL Data Packet completo, buffer size: {len(data)}, required: {offset + 24}")
                return None

            timestamp = struct.unpack('!Q', data[offset:offset+8])[0]
            print(f"Timestamp: {timestamp}")

            priority = data[offset+8]
            print(f"Priority: {priority}")

            longitude = struct.unpack('!i', data[offset+9:offset+13])[0]
            print(f"Longitude: {longitude}")

            latitude = struct.unpack('!i', data[offset+13:offset+17])[0]
            print(f"Latitude: {latitude}")

            altitude = struct.unpack('!H', data[offset+17:offset+19])[0]
            print(f"Altitude: {altitude}")

            angle = struct.unpack('!H', data[offset+19:offset+21])[0]
            print(f"Angle: {angle}")

            satellites = data[offset+21]
            print(f"Satellites: {satellites}")

            speed = struct.unpack('!H', data[offset+22:offset+24])[0]
            print(f"Speed: {speed}")

            offset += 24

            if len(data) < offset + 2:
                print("Datos insuficientes para extraer el ID de evento y el total de IO")
                return None

            event_id = data[offset]
            print(f"Event ID: {event_id}")

            total_io_elements = data[offset+1]
            print(f"Total IO Elements: {total_io_elements}")

            offset += 2

            io_elements = {}

            def read_io_elements(io_size, data_format, element_name):
                nonlocal offset
                io_elements[element_name] = {}
                io_count = data[offset]
                print(f"{element_name} IO Elements Count: {io_count}")
                offset += 1
                for _ in range(io_count):
                    io_id = data[offset]
                    io_value = struct.unpack(data_format, data[offset+1:offset+1+struct.calcsize(data_format)])[0]
                    print(f"{element_name} IO Element - ID: {io_id}, Value: {io_value}")
                    io_elements[element_name][io_id] = io_value
                    offset += struct.calcsize(data_format) + 1

            read_io_elements(1, '!B', '1B')
            read_io_elements(2, '!H', '2B')
            read_io_elements(4, '!I', '4B')
            #read_io_elements(8, '!Q', '8B')

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

        if len(data) < offset + 4:
            print("Datos insuficientes para leer el CRC")
            return None

        crc = struct.unpack('!I', data[-4:])[0]
        print(f"CRC: {crc}")

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
            buffer = b''

            data = client_socket.recv(1024)
            if data:
                print(f"Datos recibidos: {data}")
                print(f"Datos recibidos (hex): {data.hex()}")

                imei_length_hex = data[:2]
                imei_length = int(imei_length_hex.hex(), 16)
                imei_hex = data[2:2+imei_length]
                imei = imei_hex.decode('ascii')
                print(f"IMEI recibido: {imei}")

                if len(imei) == 15 and imei.isdigit():
                    print("IMEI válido")
                    
                    confirmation_message = b'\x01'
                    try:
                        client_socket.sendall(confirmation_message)
                        print("Mensaje de confirmación enviado correctamente")

                        messages_received = 0
                        while messages_received < 2:
                            new_data = client_socket.recv(1024)
                            if new_data:
                                buffer += new_data
                                messages_received += 1
                            else:
                                print("El dispositivo ha cerrado la conexión")
                                break

                        print(f"Datos acumulados en el buffer: {buffer.hex()}")
                        print(f"Tamaño final del buffer: {len(buffer)} bytes")
                        parsed_data = parse_codec8_extended(buffer)
                        if parsed_data:
                            print(f"Datos analizados: {parsed_data}")

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

if __name__ == "__main__":
    start_server()
