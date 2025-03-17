import struct

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

            avl_data_list.append({
                "timestamp": timestamp,
                "priority": priority,
                "longitude": longitude,
                "latitude": latitude,
                "altitude": altitude,
                "angle": angle,
                "satellites": satellites,
                "speed": speed
            })

        if len(data) < offset + 4:
            return None

        crc = struct.unpack('!I', data[-4:])[0]

        # Seleccionar el dato más reciente por timestamp
        if avl_data_list:
            latest_data = max(avl_data_list, key=lambda x: x["timestamp"])
        else:
            latest_data = {
                "latitude": 0,
                "longitude": 0,
                "altitude": 0,
                "angle": 0,
                "speed": 0
            }

        latest_data["imei"] = imei

        return {
            "preamble": preamble,
            "data_field_length": data_field_length,
            "codec_id": codec_id,
            "number_of_data": number_of_data,
            "avl_data_list": avl_data_list,
            "crc": crc,
            "latest_data": latest_data
        }
    except struct.error as e:
        print(f"Error al deserializar los datos: {e}")
        return None
