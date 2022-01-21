from enum import Enum
import asyncio
import bleak

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

async def send_connectionless_cmd(mac_address, cmd_code: Toa_Cmd_Code, payload: bytes) -> bytes:
    async with bleak.BleakClient(mac_address) as client:
        shared_data = None
        async def rsp_handler(sender, data):
          nonlocal shared_data
          shared_data = data
          await client.stop_notify(TILE_TOA_RSP_UUID)
    
        # issue TOA command
        await client.write_gatt_char(TILE_TOA_CMD_UUID, TOA_CONNECTIONLESS_CID + b"\x00\x00\x00\x00" + cmd_code.value + payload)

        await client.start_notify(TILE_TOA_RSP_UUID, rsp_handler)

        while shared_data is None:
          await asyncio.sleep(0.1)
        
        return shared_data

async def send_channel_cmd(mac_address, channel_id: bytes, cmd_code: Toa_Cmd_Code, payload: bytes) -> bytes:
    async with bleak.BleakClient(mac_address) as client:
        shared_data = None
        async def rsp_handler(sender, data):
          nonlocal shared_data
          shared_data = data
          await client.stop_notify(TILE_TOA_RSP_UUID)
    
        # issue TOA command
        await client.write_gatt_char(TILE_TOA_CMD_UUID, channel_id + b"\x00\x00\x00\x00" + cmd_code.value + payload)

        await client.start_notify(TILE_TOA_RSP_UUID, rsp_handler)

        while shared_data is None:
          await asyncio.sleep(0.1)
        
        return shared_data