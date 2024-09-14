import socket
import struct
import binascii
from crc16 import crc16xmodem  # Necesitarás instalar la librería crc16

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

                        while len(buffer) < 1269:
                            new_data = client_socket.recv(1024)
                            if new_data:
                                buffer += new_data
                                print(f"Nuevos datos recibidos (hex): {new_data.hex()}")
                                print(f"Tamaño acumulado del buffer: {len(buffer)} bytes")
                            else:
                                print("El dispositivo ha cerrado la conexión")
                                break

                        if len(buffer) == 1269:
                            print(f"Datos acumulados en el buffer (1269 bytes): {buffer.hex()}")
                            process_buffer(buffer)
                        else:
                            print(f"El tamaño del buffer no es el esperado: {len(buffer)} bytes")

                    except Exception as e:
                        print(f"Error al enviar el mensaje de confirmación: {e}")
                else:
                    print("IMEI inválido")
            else:
                print("El dispositivo ha cerrado la conexión")
        finally:
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

def process_buffer(buffer):
    if len(buffer) < 4:
        print("Buffer demasiado corto para procesar")
        return

    preamble = buffer[:4]
    data_field_length = struct.unpack('>I', buffer[4:8])[0]
    codec_id = buffer[8]
    num_data_1 = buffer[9]
    avl_data = buffer[10:-5]
    num_data_2 = buffer[-5]
    crc = buffer[-4:]

    print(f"Preamble: {binascii.hexlify(preamble)}")
    print(f"Data Field Length: {data_field_length}")
    print(f"Codec ID: {codec_id}")
    print(f"Number of Data 1: {num_data_1}")
    print(f"AVL Data: {binascii.hexlify(avl_data)}")
    print(f"Number of Data 2: {num_data_2}")
    print(f"CRC-16: {binascii.hexlify(crc)}")

    # Verificar CRC-16
    expected_crc = crc16xmodem(buffer[4:-4])
    actual_crc = struct.unpack('>H', crc)[0]

    if expected_crc != actual_crc:
        print("CRC-16 inválido")
        return

    print("CRC-16 válido")

    # Procesar AVL Data
    offset = 0
    while offset < len(avl_data):
        timestamp = struct.unpack('>Q', avl_data[offset:offset+8])[0]
        priority = avl_data[offset+8]
        longitude = struct.unpack('>I', avl_data[offset+9:offset+13])[0]
        latitude = struct.unpack('>I', avl_data[offset+13:offset+17])[0]
        altitude = struct.unpack('>H', avl_data[offset+17:offset+19])[0]
        angle = struct.unpack('>H', avl_data[offset+19:offset+21])[0]
        satellites = avl_data[offset+21]
        speed = struct.unpack('>H', avl_data[offset+22:offset+24])[0]
        event_io_id = struct.unpack('>H', avl_data[offset+24:offset+26])[0]
        total_id = avl_data[offset+26]
        n1_io = avl_data[offset+27]
        io1_id = struct.unpack('>H', avl_data[offset+28:offset+30])[0]
        io1_value = avl_data[offset+30]
        n2_io = avl_data[offset+31]
        io2_id = struct.unpack('>H', avl_data[offset+32:offset+34])[0]
        io2_value = struct.unpack('>H', avl_data[offset+34:offset+36])[0]
        n4_io = avl_data[offset+36]
        io4_id = struct.unpack('>H', avl_data[offset+37:offset+39])[0]
        io4_value = struct.unpack('>I', avl_data[offset+39:offset+43])[0]
        n8_io = avl_data[offset+43]
        io8_id = struct.unpack('>H', avl_data[offset+44:offset+46])[0]
        io8_value = avl_data[offset+46:offset+54]  # 8 bytes

        print(f"Timestamp: {timestamp}")
        print(f"Priority: {priority}")
        print(f"Longitude: {longitude}")
        print(f"Latitude: {latitude}")
        print(f"Altitude: {altitude}")
        print(f"Angle: {angle}")
        print(f"Satellites: {satellites}")
        print(f"Speed: {speed}")
        print(f"Event IO ID: {event_io_id}")
        print(f"Total ID: {total_id}")
        print(f"N1 IO: {n1_io}")
        print(f"IO1 ID: {io1_id}")
        print(f"IO1 Value: {io1_value}")
        print(f"N2 IO: {n2_io}")
        print(f"IO2 ID: {io2_id}")
        print(f"IO2 Value: {io2_value}")
        print(f"N4 IO: {n4_io}")
        print(f"IO4 ID: {io4_id}")
        print(f"IO4 Value: {io4_value}")
        print(f"N8 IO: {n8_io}")
        print(f"IO8 ID: {io8_id}")
        print(f"IO8 Value: {binascii.hexlify(io8_value)}")

        # Avanzar el offset basado en el tamaño de los elementos
        # Ajusta el avance del offset según los datos reales y el formato exacto
        offset += 54 + len(io8_value)  # Ajusta el tamaño total según el formato exacto

if __name__ == "__main__":
    start_server()
