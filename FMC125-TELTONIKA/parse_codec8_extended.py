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
        fuelInfo = [] 
        alarmInfo = []
        ignitionInfo = []
        v463 = []
        v464 = []

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
                io_value = struct.unpack('!I', data[offset+2:offset+6])[0]
                io_elements[io_id] = io_value
                offset += 6

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
                "io_elements": io_elements
            })

        if len(data) < offset + 4:
            return None

        crc = struct.unpack('!I', data[-4:])[0]

        # Encontrar el dato más reciente por timestamp
        latest_data = max(avl_data_list, key=lambda x: x["timestamp"], default=None)
        
        if latest_data:
            latest_data["imei"] = imei
            latest_data["fuelInfo"] = fuelInfo[-1] if fuelInfo else 0
            latest_data["alarmInfo"] = alarmInfo[-1] if alarmInfo else 0
            latest_data["ignitionInfo"] = ignitionInfo[-1] if ignitionInfo else 0
            latest_data["v463"] = v463[-1] if v463 else 0
            latest_data["v464"] = v464[-1] if v464 else 0
        
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
