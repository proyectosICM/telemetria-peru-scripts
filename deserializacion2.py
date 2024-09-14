import socket
import struct

def hex_to_bytes(hex_str):
    """Convierte una cadena hexadecimal en datos binarios."""
    return bytes.fromhex(hex_str)

def parse_codec8_extended(data):
    # Convierte los datos de hexadecimal a binario si es necesario
    if isinstance(data, str):
        data = hex_to_bytes(data)

    # Verifica si la longitud de los datos es suficiente
    if len(data) < 12:
        print("Datos incompletos")
        return None

    # Desempaqueta la cabecera
    try:
        preamble = data[:4]
        data_field_length = struct.unpack('!I', data[4:8])[0]  # Cambiado a 4 bytes
        codec_id = data[8]
        number_of_data = data[9]

        offset = 10
        avl_data_list = []

        for _ in range(number_of_data):
            if len(data) < offset + 24:  # Ajustar el tamaño del paquete AVL según el protocolo
                print(f"Datos insuficientes para extraer un AVL Data Packet completo, buffer size: {len(data)}, required: {offset + 24}")
                return None

            timestamp = struct.unpack('!Q', data[offset:offset+8])[0]  # Timestamp en milisegundos
            priority = data[offset+8]

            longitude = struct.unpack('!i', data[offset+9:offset+13])[0]  # Longitud
            latitude = struct.unpack('!i', data[offset+13:offset+17])[0]  # Latitud
            altitude = struct.unpack('!H', data[offset+17:offset+19])[0]  # Altitud
            angle = struct.unpack('!H', data[offset+19:offset+21])[0]     # Ángulo
            satellites = data[offset+21]                                 # Número de satélites
            speed = struct.unpack('!H', data[offset+22:offset+24])[0]    # Velocidad

            offset += 24

            # Número de elementos IO
            if len(data) < offset + 2:
                print("Datos insuficientes para extraer el ID de evento y el total de IO")
                return None

            event_id = data[offset]
            total_io_elements = data[offset+1]
            offset += 2

            io_elements = {}

            # Lectura de IO elements
            io_elements['1B'] = {}
            if len(data) < offset + 1:
                print("Datos insuficientes para leer elementos IO de 1 byte")
                return None

            io_count_1B = data[offset]
            offset += 1
            for _ in range(io_count_1B):
                if len(data) < offset + 2:
                    print(f"Datos insuficientes para leer todos los elementos IO de 1 byte, buffer size: {len(data)}, required: {offset + 2}")
                    return None

                io_id = data[offset]
                io_value = data[offset+1]
                io_elements['1B'][io_id] = io_value
                offset += 2

            io_elements['2B'] = {}
            if len(data) < offset + 1:
                print("Datos insuficientes para leer elementos IO de 2 bytes")
                return None

            io_count_2B = data[offset]
            offset += 1
            for _ in range(io_count_2B):
                if len(data) < offset + 3:
                    print(f"Datos insuficientes para leer todos los elementos IO de 2 bytes, buffer size: {len(data)}, required: {offset + 3}")
                    return None

                io_id = data[offset]
                io_value = struct.unpack('!H', data[offset+1:offset+3])[0]
                io_elements['2B'][io_id] = io_value
                offset += 3

            io_elements['4B'] = {}
            if len(data) < offset + 1:
                print("Datos insuficientes para leer elementos IO de 4 bytes")
                return None

            io_count_4B = data[offset]
            offset += 1
            for _ in range(io_count_4B):
                if len(data) < offset + 5:
                    print(f"Datos insuficientes para leer todos los elementos IO de 4 bytes, buffer size: {len(data)}, required: {offset + 5}")
                    return None

                io_id = data[offset]
                io_value = struct.unpack('!I', data[offset+1:offset+5])[0]
                io_elements['4B'][io_id] = io_value
                offset += 5

            io_elements['8B'] = {}
            if len(data) < offset + 1:
                print("Datos insuficientes para leer elementos IO de 8 bytes")
                return None

            io_count_8B = data[offset]
            offset += 1
            for _ in range(io_count_8B):
                if len(data) < offset + 9:
                    print(f"Datos insuficientes para leer todos los elementos IO de 8 bytes, buffer size: {len(data)}, required: {offset + 9}")
                    return None

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

        if len(data) < offset + 4:
            print("Datos insuficientes para leer el CRC")
            return None

        crc = struct.unpack('!I', data[-4:])[0]  # CRC

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
            imei_received = False

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Acumula los datos en el buffer
                buffer += data
                
                # Si no se ha recibido el IMEI completo aún
                if not imei_received:
                    if len(buffer) < 2:
                        print("Esperando datos para el IMEI")
                        continue

                    imei_length_hex = buffer[:2]
                    imei_length = int(imei_length_hex.hex(), 16)
                    if len(buffer) < 2 + imei_length:
                        print("Esperando datos completos del IMEI")
                        continue

                    imei_hex = buffer[2:2+imei_length]
                    imei = imei_hex.decode('ascii')

                    if len(imei) == 15 and imei.isdigit():
                        print(f"IMEI recibido: {imei}")
                        confirmation_message = b'\x01'
                        client_socket.sendall(confirmation_message)
                        imei_received = True
                        buffer = buffer[2+imei_length:]
                    else:
                        print("IMEI inválido")
                        rejection_message = b'\x00'
                        client_socket.sendall(rejection_message)
                        buffer = b''  # Vaciar el buffer
                        imei_received = False
                        break

                # Si el IMEI ya ha sido procesado, intentar analizar los datos
                if imei_received:
                    if len(buffer) < 12:
                        print("Esperando más datos para completar el análisis")
                        continue
                    
                    parsed_data = parse_codec8_extended(buffer)
                    if parsed_data:
                        print(f"Datos analizados: {parsed_data}")
                        buffer = b''
                    else:
                        print("Esperando más datos para completar el análisis")

        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
