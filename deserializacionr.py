import socket
import struct
import json


def hex_to_bytes(hex_str):
    """Convierte una cadena hexadecimal en datos binarios."""
    return bytes.fromhex(hex_str)

def filter_data(data_list):
    """Filtra los datos para eliminar valores atípicos o no representativos."""
    filtered_list = []
    for data in data_list:
        if (data["latitude"] != 0 and
            data["longitude"] != 0 and
            data["altitude"] > 0 and
            data["angle"] > 0):
            filtered_list.append(data)
    return filtered_list

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

        for i in range(number_of_data):
            if len(data) < offset + 24:  # Tamaño base para el paquete AVL
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

            if len(data) < offset + 2:
                return None

            event_id = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            total_io_elements = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            io_elements = {'1B': {}, '2B': {}, '4B': {}, '8B': {}, 'XB': {}}

            for io_type in io_elements.keys():
                io_count = struct.unpack('!H', data[offset: offset+2])[0]
                offset += 2
                for _ in range(io_count):
                    io_id = struct.unpack('!H', data[offset:offset+2])[0]  # El ID siempre es de 2 bits
                    if io_type == '1B':
                        io_value = data[offset+2]  # El valor es de 1 bit
                        io_elements[io_type][io_id] = io_value
                        offset += 3
                    elif io_type == '2B':
                        io_value = struct.unpack('!H', data[offset+2:offset+4])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 4
                    elif io_type == '4B':
                        io_value = struct.unpack('!I', data[offset+2:offset+6])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 6
                    elif io_type == '8B':
                        io_value = struct.unpack('!Q', data[offset+2:offset+10])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 10
                    elif io_type == 'XB':
                        value_length = struct.unpack('!H', data[offset + 2:offset + 4])[0]
                        io_value = data[offset + 4:offset + 4 + value_length]
                        io_elements[io_type][io_id] = io_value.hex()
                        offset += 4 + value_length

            # Convertir latitud y longitud a formato decimal
            avl_data_list.append({
                "timestamp": timestamp,
                "priority": priority,
                "longitude": longitude / 1e7,  # Convertir a grados decimales
                "latitude": latitude / 1e7,   # Convertir a grados decimales
                "altitude": altitude,
                "angle": angle,
                "satellites": satellites,
                "speed": speed,
                "event_id": event_id,
                "total_io_elements": total_io_elements,
                "io_elements": io_elements
            })

        if len(data) < offset + 4:
            return None

        crc = struct.unpack('!I', data[-4:])[0]  # CRC

        # Filtrar los datos antes de calcular promedios
        filtered_avl_data_list = filter_data(avl_data_list)

        # Calcular promedios
        if filtered_avl_data_list:
            total_latitude = sum(d["latitude"] for d in filtered_avl_data_list)
            total_longitude = sum(d["longitude"] for d in filtered_avl_data_list)
            total_altitude = sum(d["altitude"] for d in filtered_avl_data_list)
            total_angle = sum(d["angle"] for d in filtered_avl_data_list)
            count = len(filtered_avl_data_list)

            averages = {
                "imei": "N/A",  # El IMEI debe ser incluido en la función que llama a `parse_codec8_extended`
                "latitude": round(total_latitude / count, 7),  # Redondear a 7 decimales
                "longitude": round(total_longitude / count, 7),  # Redondear a 7 decimales
                "altitude": int(total_altitude / count),  # Convertir a entero
                "angle": int(total_angle / count)
            }
        else:
            averages = {
                "imei": "N/A",
                "latitude": 0,
                "longitude": 0,
                "altitude": 0,
                "angle": 0
            }

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": crc,
            "averages": averages
        }
    except struct.error as e:
        print(f"Error al deserializar los datos: {e}")
        return None

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

        for i in range(number_of_data):
            if len(data) < offset + 24:  # Tamaño base para el paquete AVL
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

            if len(data) < offset + 2:
                return None

            event_id = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            total_io_elements = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            io_elements = {'1B': {}, '2B': {}, '4B': {}, '8B': {}, 'XB': {}}

            for io_type in io_elements.keys():
                io_count = struct.unpack('!H', data[offset: offset+2])[0]
                offset += 2
                for _ in range(io_count):
                    io_id = struct.unpack('!H', data[offset:offset+2])[0]  # El ID siempre es de 2 bits
                    if io_type == '1B':
                        io_value = data[offset+2]  # El valor es de 1 bit
                        io_elements[io_type][io_id] = io_value
                        offset += 3
                    elif io_type == '2B':
                        io_value = struct.unpack('!H', data[offset+2:offset+4])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 4
                    elif io_type == '4B':
                        io_value = struct.unpack('!I', data[offset+2:offset+6])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 6
                    elif io_type == '8B':
                        io_value = struct.unpack('!Q', data[offset+2:offset+10])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 10
                    elif io_type == 'XB':
                        value_length = struct.unpack('!H', data[offset + 2:offset + 4])[0]
                        io_value = data[offset + 4:offset + 4 + value_length]
                        io_elements[io_type][io_id] = io_value.hex()
                        offset += 4 + value_length

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
            return None

        crc = struct.unpack('!I', data[-4:])[0]  # CRC

          # Filtrar los datos antes de calcular promedios
        filtered_avl_data_list = filter_data(avl_data_list)

        # Calcular promedios
        if filtered_avl_data_list:
            total_latitude = sum(d["latitude"] for d in filtered_avl_data_list)
            total_longitude = sum(d["longitude"] for d in filtered_avl_data_list)
            total_altitude = sum(d["altitude"] for d in filtered_avl_data_list)
            total_angle = sum(d["angle"] for d in filtered_avl_data_list)
            count = len(filtered_avl_data_list)

            averages = {
                "imei": "N/A",  # El IMEI debe ser incluido en la función que llama a `parse_codec8_extended`
                "latitude": int(total_latitude / count),  # Convertir a entero
                "longitude": int(total_longitude / count),  # Convertir a entero
                "altitude": int(total_altitude / count),  # Convertir a entero
                "angle": int(total_angle / count)  # Convertir a entero
            }
        else:
            averages = {
                "imei": "N/A",
                "latitude": 0,
                "longitude": 0,
                "altitude": 0,
                "angle": 0
            }

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": crc,
            "averages": averages
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
                        print(f"Datos acumulados en el buffer: {buffer.hex()}")
                        print(f"Tamaño final del buffer: {len(buffer)} bytes")
                        parsed_data = parse_codec8_extended(buffer)
                        if parsed_data:
                            # Incluir el IMEI en los resultados promedios
                            parsed_data['averages']['imei'] = imei
                            # Imprimir el JSON con los resultados promedios
                            print("Datos promedios:")
                            print(json.dumps(parsed_data['averages'], indent=4))

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
