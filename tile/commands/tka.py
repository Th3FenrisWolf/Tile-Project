from toa import Toa_Cmd_Code, send_channel_cmd
from enum import Enum

class Tka_Rsp_Code(Enum):
    config      = b"\x01"
    read_config = b"\x02"
    check       = b"\x03"

class Tka_Cmd_Code(Enum):
    config      = b"\x01"
    read_config = b"\x02"
    ack         = b"\x03"

async def handle_tka_rsp(tile: 'Tile', rsp_payload: bytes):
    tka_rsp_code = rsp_payload[0:1]
    if tka_rsp_code == Tka_Rsp_Code.check.value:
        # respond to check with ack
        await send_channel_cmd(tile, Toa_Cmd_Code.TKA, Tka_Cmd_Code.ack.value)
    else:
        print(f"Unhandled tka_rsp_code {tka_rsp_code}")