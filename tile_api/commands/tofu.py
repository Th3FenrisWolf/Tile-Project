from io import BytesIO
from crc import crc16
from toa import Toa_Cmd_Code, send_channel_cmd
from enum import Enum
import asyncio

# Print Debug information for this file (T/F):
debug = True

# CMD

class Tofu_Ctl_Cmd(Enum):
    DATA   = b"\x00"
    RESUME = b"\x01"
    EXIT   = b"\x02"

async def request_tofu_ready(tile: 'Tile', firmware_version: str, img_len: int):

    assert (len(firmware_version) == 10 ), "Firmware version str must be 10 bytes!"

    payload = Tofu_Ctl_Cmd.RESUME.value + firmware_version.encode() + img_len.to_bytes(3, "little")
    await send_channel_cmd(tile, Toa_Cmd_Code.TOFU_CTL, payload)


# RSP

class Tofu_Ctl_Rsp(Enum):
    RESUME_READY = b"\x01"
    BLOCK_OK     = b"\x02"
    IMAGE_OK     = b"\x03"
    EXIT_OK      = b"\x04"
    ERROR        = b"\x20" 


def handle_tofu_ctl_rsp(tile: 'Tile', rsp_payload: bytes):
    tofu_ctl_rsp_code = rsp_payload[0:1]
    if tofu_ctl_rsp_code == Tofu_Ctl_Rsp.RESUME_READY.value:
        tile._block_length = int.from_bytes(rsp_payload[1:5], byteorder="little")
        tile._image_index = int.from_bytes(rsp_payload[5:9], byteorder="little")
        if debug : print(f"block_length={tile._block_length} image_index={tile._image_index}")
        tile._tofu_ctl_resume_ready_rsp_evt.set()
    elif tofu_ctl_rsp_code == Tofu_Ctl_Rsp.BLOCK_OK.value:
        tile._tofu_ctl_block_ready_rsp_evt.set()

async def upload_firmware(tile: 'Tile', file_path: str):
    # ensure that the resume ready rsp has been gotten
    await tile._tofu_ctl_resume_ready_rsp_evt.wait()

    # bytes (20 - mic (4) - channel_id (1) - cmd_code (1))
    MAX_DATA_PAYLOAD = 14

    with open(file_path, "rb") as f:
        block_num = 0
        while len(block := f.read(tile._block_length)):
            if debug : print(f"--------------------{block_num}------------------")
            crc16_bytes = crc16(0, block).to_bytes(2, 'little')
            block_io = BytesIO(block + crc16_bytes)
            while len(packet := block_io.read(MAX_DATA_PAYLOAD)):
                await send_channel_cmd(tile, Toa_Cmd_Code.TOFU_DATA, packet)
            # sent block number
            block_num += 1
            # wait for response from tile
            await tile._tofu_ctl_block_ready_rsp_evt.wait()
            tile._tofu_ctl_block_ready_rsp_evt.clear()
    await asyncio.sleep(10)
