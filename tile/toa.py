from enum import Enum
import asyncio
from time import sleep

# constants defined within tile_lib.h
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# Channel ID (CID) for TOA connectionless channel defined in toa.h:104
TOA_CONNECTIONLESS_CID = b"\x00"

class Toa_Cmd_Code(Enum):
    TOFU_CTL      = b"\x01"
    TOFU_DATA     = b"\x02"
    BDADDR        = b"\x03"
    TDT           = b"\x04" 
    SONG          = b"\x05" 
    PPM           = b"\x06" 
    ADV_INT       = b"\x07"
    TKA           = b"\x08"
    TAC           = b"\x09" 
    TDG           = b"\x0a" 
    TMD           = b"\x0b" 
    TCU           = b"\x0c" 
    TIME          = b"\x0d" 
    TEST          = b"\x0e" 
    TFC           = b"\x0f" 
    OPEN_CHANNEL  = b"\x10"
    CLOSE_CHANNEL = b"\x11"
    READY         = b"\x12"
    TDI           = b"\x13" 
    AUTHENTICATE  = b"\x14"
    TMF           = b"\x15" 
    TLIL          = b"\x16" 
    TEF           = b"\x17"
    TRM           = b"\x18"
    TPC           = b"\x19"
    ASSOCIATE     = b"\x1A"

async def send_connectionless_cmd(client, cmd_code: Toa_Cmd_Code, payload: bytes) -> bytes:
    try:
        await client.connect()

        await asyncio.sleep(0.2)

        # issue TOA command
        await client.write_gatt_char(TILE_TOA_CMD_UUID, TOA_CONNECTIONLESS_CID + b"\x00\x00\x00\x00" + cmd_code.value + payload)

        await asyncio.sleep(0.2)

        # get TOA response
        return await client.read_gatt_char(TILE_TOA_RSP_UUID)
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()