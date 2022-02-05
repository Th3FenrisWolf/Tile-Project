from enum import Enum
from time import sleep
from toa import Toa_Cmd_Code, send_channel_cmd
import hashlib
import hmac
import asyncio

# referenced in tile_song_module.h:216
class Strength(Enum):
    SILENT = b"\x00"
    LOW = b"\x01"
    MEDIUM = b"\x02"
    HIGH = b"\x03"

# referenced in tile_song_module.h:38
class Songs(Enum):
    CLICK_1      = b"\x00"
    FIND         = b"\x01"
    ACTIVE       = b"\x02"
    SLEEP        = b"\x03"
    WAKEUP       = b"\x04"
    FACTORY_TEST = b"\x05"
    MYSTERY      = b"\x06"
    SILENT       = b"\x07"
    BUTTON       = b"\x08"
    WAKEUP_PART  = b"\x09"
    DT_SUCCESS   = b"\x0a"
    DT_FAILURE   = b"\x0b"
    CLICK_2      = b"\x0c"
    BIP_1        = b"\x0d"
    BIP_2        = b"\x0e"
    BIP_3        = b"\x0f"
    BIP_4        = b"\x10"
    BIP_5        = b"\x11"
    BIP_6        = b"\x12"
    BIP_7        = b"\x13"
    DT_HB        = b"\x14"
    MAX          = b"\x15"
    STOP         = b"\xFF"

# the implicit duration is 0xfe, which appears to just play the song in its entirety
# strength ranges from 0-3, where 0 is silent and 3 is loudest
# according to tile_song_module.h:214
async def request_ring(tile: 'Tile', song_number: bytes, strength: bytes) -> None:
    toa_cmd_payload = b"\x02" + song_number + strength
    await send_channel_cmd(tile, Toa_Cmd_Code.SONG, toa_cmd_payload)