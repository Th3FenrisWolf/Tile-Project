from toa import Toa_Cmd_Code, send_channel_cmd
from enum import Enum

# CMD

class Tofu_Ctl_Cmd(Enum):
    DATA   = b"\x00"
    RESUME = b"\x01"
    EXIT   = b"\x02"

async def request_tofu_ready(tile: 'Tile', firmware_version: str, img_len: int):

    assert (len(firmware_version) == 10 ), "Firmware version str must be 10 bytes!"

    payload = Tofu_Ctl_Cmd.RESUME + firmware_version.encode() + img_len.to_bytes(3, "little")
    await send_channel_cmd(tile, Toa_Cmd_Code.TOFU_CTL, payload)


async def send_tofu_data(tile: 'Tile', data: bytes):
    await send_channel_cmd(tile, Toa_Cmd_Code.TOFU_DATA, data)

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
        tile._tofu_ctl_resume_ready_rsp_evt.set()

def upload_firmware(tile: 'Tile', file_path: str, file_size: int):
    # ensure that the resume ready rsp has been gotten
    tile._tofu_ctl_resume_ready_rsp_evt.wait()

  # bytes (20 - mic (4) - channel_id (1) - cmd_code (1))
    MAX_DATA_PAYLOAD = 14

    bytes_left_to_write = file_size

    with open(file_path) as f:
        block = f.read(tile._block_length if bytes_left_to_write > tile._block_length else bytes_left_to_write)
        for packet in range(len(block) / MAX_DATA_PAYLOAD):
            send_channel_cmd(tile, Tofu_Ctl_Cmd.DATA, packet)
        #assuming that it'll correctly read the block and split it up correctly 
        #await handle_tofu_ctl_rsp(tile, Tofu_Ctl_Rsp.BLOCK_OK)
            





