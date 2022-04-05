from enum import Enum
from time import sleep
import asyncio
from io import BytesIO

# Print Debug information for this file (T/F):
debug = False

# referenced in tile_song_module.h:216
class Strength(Enum):
    SILENT = b"\x00"
    LOW = b"\x01"
    MEDIUM = b"\x02"
    HIGH = b"\x03"

# referenced in tile_song_module.h:38
class Songs(Enum):
    CLICK_1      = b"\x00"
    FIND         = b"\x01" # this song is overwritten with custom song
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

class Song_Cmd_Code(Enum):
    READ_FEATURES = b"\x01"
    PLAY          = b"\x02"
    STOP          = b"\x03"
    PROGRAM       = b"\x04"
    DATA          = b"\x05"
    READ_SONG_MAP = b"\x06"

class Song_Rsp_Code(Enum):
    READ_FEATURES_OK = b"\x01"
    PLAY_OK          = b"\x02"
    STOP_OK          = b"\x03"
    PROGRAM_READY    = b"\x04"
    BLOCK_OK         = b"\x05"
    PROGRAM_COMPLETE = b"\x06"
    SONG_MAP         = b"\x07"
    QUALITY          = b"\x08"
    ERROR            = b"\x20"


def handle_song_rsp(tile: 'Tile', rsp_payload: bytes):
    song_rsp_code = rsp_payload[0:1]
    if song_rsp_code == Song_Rsp_Code.PROGRAM_READY.value:
        tile._song_block_length = int.from_bytes(rsp_payload[1:2], byteorder="little")
        if debug : print(f"song_block_length={tile._song_block_length}")
        tile._song_program_ready_rsp_evt.set()
    elif song_rsp_code == Song_Rsp_Code.BLOCK_OK.value:
        tile._song_block_ok_rsp_evt.set()
    elif song_rsp_code == Song_Rsp_Code.PLAY_OK.value:
        tile._song_play_ok_rsp_evt.set()
    elif song_rsp_code == Song_Rsp_Code.PROGRAM_COMPLETE.value:
        tile._song_block_ok_rsp_evt.set()
    elif song_rsp_code == Song_Rsp_Code.SONG_MAP.value:
        tile._curr_song_id = int.from_bytes(rsp_payload[2:4], byteorder='little')
        tile._song_map_rsp_evt.set()
    else:
        if debug : print(f"not handling song rsp {song_rsp_code.hex()}")

# the implicit duration is 0xfe, which appears to just play the song in its entirety
# strength ranges from 0-3, where 0 is silent and 3 is loudest
# according to tile_song_module.h:214
async def request_ring_and_wait_response(tile: 'Tile', song_number: bytes, strength: bytes) -> None:
    from toa import Toa_Cmd_Code, send_channel_cmd
    tile._song_play_ok_rsp_evt = asyncio.Event()
    toa_cmd_payload = Song_Cmd_Code.PLAY.value + song_number + strength
    await send_channel_cmd(tile, Toa_Cmd_Code.SONG, toa_cmd_payload)
    # wait for response before returning
    await tile._song_play_ok_rsp_evt.wait()


async def request_song_program(tile: 'Tile', file_size: int):
    from toa import Toa_Cmd_Code, send_channel_cmd
    # our research showed this must be 1
    song_index_to_overwrite = (1).to_bytes(1, 'little')
    payload = Song_Cmd_Code.PROGRAM.value + song_index_to_overwrite + file_size.to_bytes(2, "little")
    await send_channel_cmd(tile, Toa_Cmd_Code.SONG, payload)

async def request_read_song_map(tile: 'Tile'):
    from toa import Toa_Cmd_Code, send_channel_cmd
    await send_channel_cmd(tile, Toa_Cmd_Code.SONG, Song_Cmd_Code.READ_SONG_MAP.value)

async def upload_custom_song(tile: 'Tile', file_path: str):
    from crc import crc16
    from toa import Toa_Cmd_Code, send_channel_cmd
    # ensure that the resume ready rsp has been gotten
    await tile._song_program_ready_rsp_evt.wait()

    # bytes (20 - mic (4) - channel_id (1) - cmd_code (1) - song_cmd_code (1))
    MAX_DATA_PAYLOAD = 13

    with open(file_path, "rb") as f:
        block_num = 0
        while len(block := f.read(tile._song_block_length)):
            if debug : print(f"--------------------{block_num}------------------")
            crc16_bytes = crc16(0, block).to_bytes(2, 'little')
            block_io = BytesIO(block + crc16_bytes)
            while len(packet := block_io.read(MAX_DATA_PAYLOAD)):
                packet = Song_Cmd_Code.DATA.value + packet
                await send_channel_cmd(tile, Toa_Cmd_Code.SONG, packet)
            # sent block number
            block_num += 1
            # wait for response from tile
            await tile._song_block_ok_rsp_evt.wait()
            tile._song_block_ok_rsp_evt.clear()