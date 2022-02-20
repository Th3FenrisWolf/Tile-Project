def crc16(crc: int, data: bytes, poly=0x8408):
    data = bytearray(data)
    for b in data:
        cur_byte = 0xFF & b
        crc &= 0xFFFF
        crc ^= cur_byte
        for _ in range(8):
            if (crc & 0x0001) == 0:
                crc >>= 1
                crc &= 0xFFFF
            else:
                crc = (((crc >> 1) & 0xFFFF) ^ poly) & 0xFFFF
    
    return crc & 0xFFFF