import struct
import logging
from datetime import datetime

# Configuración básica del logger
#logging.basicConfig(filename='errors.log', level=logging.ERROR, 
#                    format='%(asctime)s - IMEI: %(imei)s - %(message)s', 
#                    datefmt='%Y-%m-%d %H:%M:%S')

def filter_data(data_list):
    """Filtra los datos para eliminar valores atípicos o no representativos."""
    # Excluir datos con coordenadas inválidas
    valid_data = [
        data for data in data_list
        if data["latitude"] != 0 and data["longitude"] != 0 and data["altitude"] > 0
    ]

    if not valid_data:
        return []

    # Extraer los valores de speed
    speeds = [data["speed"] for data in valid_data]

    # Si todos los valores de speed son 0, mantenerlos
    if all(speed == 0 for speed in speeds):
        return valid_data

    # Identificar la mayoría de valores similares (tolerancia: +-5)
    def is_similar(val1, val2, tolerance=5):
        return abs(val1 - val2) <= tolerance

    # Determinar el valor más frecuente (dentro del rango de tolerancia)
    similar_groups = {}
    for speed in speeds:
        if speed == 0:  # Ignorar temporalmente los valores 0
            continue
        matched = False
        for key in similar_groups:
            if is_similar(speed, key):
                similar_groups[key].append(speed)
                matched = True
                break
        if not matched:
            similar_groups[speed] = [speed]

    # Encontrar el grupo mayoritario
    majority_speed_group = max(similar_groups.values(), key=len, default=[])

    # Si la mayoría es consistente, filtrar los datos
    filtered_list = [
        data for data in valid_data
        if data["speed"] == 0 or data["speed"] in majority_speed_group
    ]

    return filtered_list

def parse_codec8_extended(data, imei):
    # Convierte los datos de hexadecimal a binario si es necesario

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
        fuelInfo = [] 
        alarmInfo = []
        ignitionInfo = []
        v463 = []
        v464 = []

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
                        #print(f"IO Type: {io_type}, IO ID: {io_id}, IO Value: {io_value}")
                    elif io_type == '8B':
                        io_value = struct.unpack('!Q', data[offset+2:offset+10])[0]
                        io_elements[io_type][io_id] = io_value
                        offset += 10
                        #print(f"IO Type: {io_type}, IO ID: {io_id}, IO Value: {io_value}")
                    elif io_type == 'XB':
                        value_length = struct.unpack('!H', data[offset + 2:offset + 4])[0]
                        io_value = data[offset + 4:offset + 4 + value_length]
                        io_elements[io_type][io_id] = io_value.hex()
                        offset += 4 + value_length
                        #print(f"IO Type: {io_type}, IO ID: {io_id}, IO Value: {io_value}")
                    
                    if io_id == 270 and io_value != 0:
                        fuelInfo.append(io_value)
                    
                    if io_id == 1 and io_value != 0:
                        alarmInfo.append(io_value)
                        
                    if io_id == 239 and io_value != 0:
                        ignitionInfo.append(io_value)
                        
                    if io_id == 463 and io_value != 0:
                        v463.append(io_value)
                        
                    if io_id == 464 and io_value != 0:
                        v464.append(io_value)
                        
                    

            # Convertir latitud y longitud a formato decimal
            avl_data_list.append({
                "timestamp": timestamp,
                "priority": priority,
                "longitude": longitude / 1e7,  # Convertir a grados decimales
                "latitude": latitude / 1e7,   # Convertir a grados de
                "altitude": altitude,
                "angle": angle,
                "satellites": satellites,
                "speed": speed,
                "event_id": event_id,
                "total_io_elements": total_io_elements,
                "io_elements": io_elements
            })
            
            #print(f"Datos Extraidos AVL: {avl_data_list}")

        if len(data) < offset + 4:
            return None

        crc = struct.unpack('!I', data[-4:])[0]  # CRC
        #print(f"crc: {crc}")
        # Filtrar los datos antes de calcular promedios
        latest_avl = max(avl_data_list, key=lambda x: x["timestamp"])
        print(f"Data AVL: {latest_avl}")
        filtered_avl_data_list = filter_data(avl_data_list)

        # Calcular promedios
        if latest_avl:

            def get_io_value(io_elements, io_id):
                """Busca el valor de un IO en todas las categorías disponibles."""
                for key in io_elements:
                    if io_id in io_elements[key]:
                        return io_elements[key][io_id]
                return 0  # Valor por defecto si no se encuentra

            latest_data = {
                "imei": imei,
                "latitude": latest_avl["latitude"],
                "longitude": latest_avl["longitude"],
                "altitude": latest_avl["altitude"],
                "angle": latest_avl["angle"],
                "speed": latest_avl["speed"],
                "fuelInfo": get_io_value(latest_avl["io_elements"], 270),
                "alarmInfo": get_io_value(latest_avl["io_elements"], 1),
                "ignitionInfo": get_io_value(latest_avl["io_elements"], 239),
                "v463": get_io_value(latest_avl["io_elements"], 463),
                "v464": get_io_value(latest_avl["io_elements"], 464)
            }
        else:
            averages = {
                "imei": "N/A",
                "latitude": 0,
                "longitude": 0,
                "altitude": 0,
                "angle": 0,
                "speed": 0,
                "fuelInfo": 0,
                "alarmInfo": 0,
                "ignitionInfo": 0,
                "v463": 0,
                "v464": 0
            }

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": crc,
            "data": latest_data
        }
    except struct.error as e:
        print(f"Error al deserializar los datos: {e}")
        #logging.error(f"Error al deserializar los datos: {e}", extra={'imei': imei})
        return None