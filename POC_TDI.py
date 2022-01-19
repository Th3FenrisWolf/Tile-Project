import asyncio
from bleak import BleakClient

import hmac
import hashlib

# specifc to our tile, acquired from ble scanning and verified in disassembly
# address = "e6:9e:55:1a:91:28"

# backpack MAC
address = "E1:5B:A3:01:A0:F1"

# constants defined within tile_lib.h
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# CID for TOA connectionless channel defined in toa.h:104
TOA_CONNECTIONLESS_CID = 0

# random byte values, required random byte as found in toa.h:295 
rand_a = b"\x00" * 14

# random byte values, required as seen in the assembly 
sres = b"\x22" * 4

class TDI_CMD:
  TILE_ID     = 0x02
  FM_VERSION  = 0x03
  MODEL_NUM   = 0x04
  HW_VERSION  = 0x05
  MAC_ADDR    = 0x06

class Toa_Cmd_Code:
  TOA_CMD_TOFU_CTL      = 0x01
  TOA_CMD_TOFU_DATA     = 0x02
  TOA_CMD_BDADDR        = 0x03
  TOA_CMD_TDT           = 0x04 
  TOA_CMD_SONG          = 0x05 
  TOA_CMD_PPM           = 0x06 
  TOA_CMD_ADV_INT       = 0x07
  TOA_CMD_TKA           = 0x08
  TOA_CMD_TAC           = 0x09 
  TOA_CMD_TDG           = 0x0a 
  TOA_CMD_TMD           = 0x0b 
  TOA_CMD_TCU           = 0x0c 
  TOA_CMD_TIME          = 0x0d 
  TOA_CMD_TEST          = 0x0e 
  TOA_CMD_TFC           = 0x0f 
  TOA_CMD_OPEN_CHANNEL  = 0x10
  TOA_CMD_CLOSE_CHANNEL = 0x11
  TOA_CMD_READY         = 0x12
  TOA_CMD_TDI           = 0x13 
  TOA_CMD_AUTHENTICATE  = 0x14
  TOA_CMD_TMF           = 0x15 
  TOA_CMD_TLIL          = 0x16 
  TOA_CMD_TEF           = 0x17
  TOA_CMD_TRM           = 0x18
  TOA_CMD_TPC           = 0x19
  TOA_CMD_ASSOCIATE     = 0x1A

async def main(address):
    async with BleakClient(address) as client:
        async def toa_open_channel_rsp_callback(sender: int, data: bytearray):
            print(data)
            return

        # set up callback handle for TOA open channel RSP
        await client.start_notify(TILE_TOA_RSP_UUID, toa_open_channel_rsp_callback)

        # set parameters for TOA open channel CMD
        cid = TOA_CONNECTIONLESS_CID.to_bytes(1, byteorder='big')
        toa_cmd = Toa_Cmd_Code.TOA_CMD_OPEN_CHANNEL.to_bytes(1, byteorder='big')

        # issue TOA open channel CMD
        await client.write_gatt_char(TILE_TOA_CMD_UUID, b"\x00\x00\x00\x00\x00\x13\x03")

asyncio.run(main(address))
