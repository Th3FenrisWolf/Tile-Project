from curses import raw
from enum import Enum
from toa import send_connectionless_cmd
from toa import Toa_Cmd_Code
import asyncio

class Tdi_Cmd_Code(Enum):
  unknown = b"\x01"
  tileID = b"\x02"
  firmwareVersion = b"\x03"
  modelNumber = b"\x04"
  hardwareVersion = b"\x05"
  mac = b"\x06"

def get_tile_id(mac_address) -> str:
    loop = asyncio.get_event_loop()
    raw_bytes = loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.TDI, Tdi_Cmd_Code.tileID.value))
    # parse raw_bytes into string and return
    return raw_bytes[7:].hex()