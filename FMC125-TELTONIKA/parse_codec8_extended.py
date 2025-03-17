import struct
import logging
from datetime import datetime

def parse_codec8_extended(data, imei):
    if len(data) < 12:
        print("Datos incompletos")
        return None

    try:
        preamble = data[:4]
        data_field_length = struct.unpack('!I', data[4:8])[0]
        codec_id = data[8]
        number_of_data = data[9]
        offset = 10
        avl_data_list = []

        for i in range(number_of_data):
            if len(data) < offset + 24:
                return None

            timestamp = struct.unpack('!Q', data[offset:offset+8])[0]  
            priority = data[offset+8]
            longitude = struct.unpack('!i', data[offset+9:offset+13])[0] / 1e7
            latitude = struct.unpack('!i', data[offset+13:offset+17])[0] / 1e7
            altitude = struct.unpack('!H', data[offset+17:offset+19])[0]
            angle = struct.unpack('!H', data[offset+19:offset+21])[0]
            satellites = data[offset+21]
            speed = struct.unpack('!H', data[offset+22:offset+24])[0]
            offset += 24

            if len(data) < offset + 2:
                return None

            event_id = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            total_io_elements = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            io_elements = {}

            for _ in range(total_io_elements):
                io_id = struct.unpack('!H', data[offset:offset+2])[0]
                io_value = struct.unpack('!I', data[offset+2:offset+6])[0]  # Ajusta según el tamaño real
                io_elements[io_id] = io_value
                offset += 6

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

        if not avl_data_list:
            return None

        # Seleccionar el AVL más reciente
        latest_avl = max(avl_data_list, key=lambda x: x["timestamp"])

        latest_data = {
            "imei": imei,
            "latitude": latest_avl["latitude"],
            "longitude": latest_avl["longitude"],
            "altitude": latest_avl["altitude"],
            "angle": latest_avl["angle"],
            "speed": latest_avl["speed"],
            "fuelInfo": latest_avl["io_elements"].get(270, 0),
            "alarmInfo": latest_avl["io_elements"].get(1, 0),
            "ignitionInfo": latest_avl["io_elements"].get(239, 0),
            "v463": latest_avl["io_elements"].get(463, 0),
            "v464": latest_avl["io_elements"].get(464, 0)
        }

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": struct.unpack('!I', data[-4:])[0],
            "data": latest_data
        }

    except struct.error as e:
        print(f"Error al deserializar los datos: {e}")
        return None
