from curses import raw
from enum import Enum
from toa import send_connectionless_cmd
from toa import Toa_Cmd_Code
import asyncio

class Tdi_Cmd_Code(Enum):
  tile_id = b"\x02"
  fw_version = b"\x03"
  model_num = b"\x04"
  hw_version = b"\x05"

def get_tile_id(mac_address) -> str:
    loop = asyncio.get_event_loop()
    raw_bytes = loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.TDI, Tdi_Cmd_Code.tile_id.value))
    # parse raw_bytes into string and return
    return raw_bytes[7:].hex()

def get_fw_version(mac_address) -> str:
    loop = asyncio.get_event_loop()
    raw_bytes = loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.TDI, Tdi_Cmd_Code.fw_version.value))
    # parse raw_bytes into string and return
    return raw_bytes[7:].decode()

def get_model_num(mac_address) -> str:
    loop = asyncio.get_event_loop()
    raw_bytes = loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.TDI, Tdi_Cmd_Code.model_num.value))
    # parse raw_bytes into string and return
    return raw_bytes[7:].decode()

def get_hw_version(mac_address) -> str:
    loop = asyncio.get_event_loop()
    raw_bytes = loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.TDI, Tdi_Cmd_Code.hw_version.value))
    # parse raw_bytes into string and return
    return raw_bytes[7:].decode()