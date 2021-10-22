import asyncio
from bleak import BleakClient

import hmac
import hashlib

address = "e6:9e:55:1a:91:28"
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# extracted from tile
AUTH_KEY = b"\x59\xbe\xca\x33\xac\x3d\x4a\x65\xc7\x1e\xeb\xca\x8d\x91\x8b\x77"

rand_a = b"\x00" * 14
sres = b"\x22" * 4

async def main(address):
    async with BleakClient(address) as client:
        async def callback(sender: int, data: bytearray):
            toa_rsp = data[5:6]
            allocated_cid = data[6:7]
            rand_t = data[7:]
            print(toa_rsp, allocated_cid, rand_t)
            message = rand_a + rand_t + allocated_cid + sres
            # only uses 16 bytes (or half of the hmac)
            session_key = hmac.new(AUTH_KEY, msg=message, digestmod = hashlib.sha256).digest()[:16]
            print(session_key)
            # now write
            toa_cmd_code = b"\05"
            # second byte is the number
            # third byte is the strength 
            toa_cmd_payload = b"\x02\05\x05"
            # necessary for mic calculations
            MAX_PAYLOAD_LEN = 22
            toa_cmd_code_and_payload_len = (len(toa_cmd_code) + len(toa_cmd_payload)).to_bytes(1, byteorder='big')
            toa_cmd_padding = (MAX_PAYLOAD_LEN - len(toa_cmd_code) - len(toa_cmd_payload)) * b"\0"
            new_message = b"\x01" + b"\x00" * 7 + b"\x01" + toa_cmd_code_and_payload_len + toa_cmd_code + toa_cmd_payload + toa_cmd_padding 
            mic = hmac.new(session_key, msg=new_message, digestmod = hashlib.sha256).digest()[:4]
            print(mic)
            play_song = allocated_cid + toa_cmd_code + toa_cmd_payload + mic
            await client.write_gatt_char(TILE_TOA_CMD_UUID, play_song)

        await client.start_notify(TILE_TOA_RSP_UUID, callback)
        cid = b"\x00"
        toa_cmd = b"\x10"
        await client.write_gatt_char(TILE_TOA_CMD_UUID, cid + sres + toa_cmd + rand_a)


asyncio.run(main(address))

# auth key = {0x59, 0xbe, 0xca, 0x33, 0xac, 0x3d, 0x4a, 0x65, 0xc7, 0x1e, 0xeb, 0xca, 0x8d, 0x91, 0x8b, 0x77}
