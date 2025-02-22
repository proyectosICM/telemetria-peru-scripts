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
        filtered_avl_data_list = filter_data(avl_data_list)

        # Calcular promedios
        if filtered_avl_data_list:
            total_latitude = sum(d["latitude"] for d in filtered_avl_data_list)
            total_longitude = sum(d["longitude"] for d in filtered_avl_data_list)
            total_altitude = sum(d["altitude"] for d in filtered_avl_data_list)
            total_angle = sum(d["angle"] for d in filtered_avl_data_list)
            total_speed = sum(d["speed"] for d in filtered_avl_data_list)
            count = len(filtered_avl_data_list)

            if fuelInfo:
                avg_io_value_270 = round(sum(fuelInfo) / len(fuelInfo), 2)  # Redondear a 2 decimales
            else:
                avg_io_value_270 = 0 
            
            if alarmInfo:
                avg_io_value_1 = round(sum(alarmInfo) / len(alarmInfo))  # Redondear a 2 decimales
            else:
                avg_io_value_1 = 0 
                
            if ignitionInfo:
                avg_io_value_239 = round(sum(ignitionInfo) / len(ignitionInfo))  # Redondear a 2 decimales
            else:
                avg_io_value_239 = 0
                
            if v463:
                avg_io_value_463 = round(sum(v463) / len(v463))
            else:
                avg_io_value_463 = 0
                
            if v464:
                avg_io_value_464 = round(sum(v464) / len(v464))
            else:
                avg_io_value_464 = 0


            averages = {
                "imei": imei,  # El IMEI debe ser incluido en la función que llama a `parse_codec8_extended`
                "latitude": round(total_latitude / count, 7),  # Redondear a 7 decimales
                "longitude": round(total_longitude / count, 7),  # Redondear a 7 decimales
                "altitude": int(total_altitude / count),  # Convertir a entero
                "angle": int(total_angle / count),
                "speed": int(total_speed / count),
                "fuelInfo": avg_io_value_270,
                "alarmInfo": avg_io_value_1,
                "ignitionInfo": avg_io_value_239,
                "v463": avg_io_value_463,
                "v464": avg_io_value_464
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
                "v463": avg_io_value_463,
                "v464": avg_io_value_464
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
        #logging.error(f"Error al deserializar los datos: {e}", extra={'imei': imei})
        return None