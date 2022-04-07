from enum import Enum
from toa import send_connectionless_cmd, Toa_Cmd_Code

# CMD

class Tdi_Cmd_Code(Enum):
  available_info = b"\x01"
  tile_id        = b"\x02"
  fw_version     = b"\x03"
  model_num      = b"\x04"
  hw_version     = b"\x05"
  bdaddr         = b"\x06"

async def send_tdi_cmd(tile: 'Tile', payload: bytes):
    await send_connectionless_cmd(tile, Toa_Cmd_Code.TDI, payload)

async def request_tile_id(tile: 'Tile'):
    await send_tdi_cmd(tile, Tdi_Cmd_Code.tile_id.value)

async def request_fw_version(tile: 'Tile') -> str:
    await send_tdi_cmd(tile, Tdi_Cmd_Code.fw_version.value)

async def request_model_num(tile: 'Tile') -> str:
    await send_tdi_cmd(tile, Tdi_Cmd_Code.model_num.value)

async def request_hw_version(tile: 'Tile') -> str:
    await send_tdi_cmd(tile, Tdi_Cmd_Code.hw_version.value)

async def request_all_tdi(tile: 'Tile'):
    await request_tile_id(tile)
    await request_fw_version(tile)
    await request_model_num(tile)
    await request_hw_version(tile)

# RSP

class Tdi_Rsp_Code(Enum):
  available_info = b"\x01"
  tile_id        = b"\x02"
  fw_version     = b"\x03"
  model_num      = b"\x04"
  hw_version     = b"\x05"
  bdaddr         = b"\x06"
  error          = b"\x20"

def handle_tdi_rsp(tile: 'Tile', rsp_payload: bytes):
    tdi_rsp_code = rsp_payload[0:1]
    if tdi_rsp_code == Tdi_Rsp_Code.tile_id.value:
        tile._tile_id = rsp_payload[1:].hex()
        tile._tile_id_rsp_evt.set()
    elif tdi_rsp_code == Tdi_Rsp_Code.fw_version.value:
        tile._fw_version = rsp_payload[1:].decode()
        tile._fw_version_rsp_evt.set()
    elif tdi_rsp_code == Tdi_Rsp_Code.model_num.value:
        tile._model_num = rsp_payload[1:].decode()
        tile._model_num_rsp_evt.set()
    elif tdi_rsp_code == Tdi_Rsp_Code.hw_version.value:
        tile._hw_version = rsp_payload[1:].decode()
        tile._hw_version_rsp_evt.set()
    else:
        print(f"Unhandled tdi_rsp_code {tdi_rsp_code}")