import asyncio
from bleak import BleakClient
from enum import Enum

import hmac
import hashlib

# specifc to our tile, acquired from ble scanning and verified in disassembly
# address = "e6:9e:55:1a:91:28"

# backpack MAC
address = "e6:9e:55:1a:91:28"

# constants defined within tile_lib.h
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# CID for TOA connectionless channel defined in toa.h:104
TOA_CONNECTIONLESS_CID = b"\x00"

# sres, required padding as seen in the assembly
SRES = b"\x00" * 4

class Toa_Cmd_Code(Enum):
  TOA_CMD_TOFU_CTL      = b"\x01"
  TOA_CMD_TOFU_DATA     = b"\x02"
  TOA_CMD_BDADDR        = b"\x03"
  TOA_CMD_TDT           = b"\x04"
  TOA_CMD_SONG          = b"\x05"
  TOA_CMD_PPM           = b"\x06"
  TOA_CMD_ADV_INT       = b"\x07"
  TOA_CMD_TKA           = b"\x08"
  TOA_CMD_TAC           = b"\x09"
  TOA_CMD_TDG           = b"\x0a"
  TOA_CMD_TMD           = b"\x0b"
  TOA_CMD_TCU           = b"\x0c"
  TOA_CMD_TIME          = b"\x0d"
  TOA_CMD_TEST          = b"\x0e"
  TOA_CMD_TFC           = b"\x0f"
  TOA_CMD_OPEN_CHANNEL  = b"\x10"
  TOA_CMD_CLOSE_CHANNEL = b"\x11"
  TOA_CMD_READY         = b"\x12"
  TOA_CMD_TDI           = b"\x13"
  TOA_CMD_AUTHENTICATE  = b"\x14"
  TOA_CMD_TMF           = b"\x15"
  TOA_CMD_TLIL          = b"\x16"
  TOA_CMD_TEF           = b"\x17"
  TOA_CMD_TRM           = b"\x18"
  TOA_CMD_TPC           = b"\x19"
  TOA_CMD_ASSOCIATE     = b"\x1A"

class Tdi_Cmd_Code(Enum):
  unknown = b"\x01"
  tileID = b"\x02"
  firmwareVersion = b"\x03"
  modelNumber = b"\x04"
  hardwareVersion = b"\x05"
  mac = b"\x06"

async def send_connectionless_cmd(address: str, cmd_code: Toa_Cmd_Code, payload: bytes):
    async with BleakClient(address) as client:
        # issue TOA command
        await client.write_gatt_char(TILE_TOA_CMD_UUID, TOA_CONNECTIONLESS_CID + SRES + cmd_code.value + payload)

        # get TOA response
        return await client.read_gatt_char(TILE_TOA_RSP_UUID)

ret = asyncio.run(send_connectionless_cmd(address, Toa_Cmd_Code.TOA_CMD_TDI, Tdi_Cmd_Code.firmwareVersion.value))
print(ret)