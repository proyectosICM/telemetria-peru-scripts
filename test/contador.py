hex_data = "0000"

# Convertir la cadena hexadecimal a bytes
buffer_bytes = bytes.fromhex(hex_data)

# Obtener el tamaño en bytes
buffer_size = len(buffer_bytes)

print(f"Tamaño del buffer: {buffer_size} bytes")
