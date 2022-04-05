from enum import Enum
import asyncio
from functools import partial
from hashlib import sha256
import hmac
import bleak

# Print Debug information for this file (T/F):
debug = False

# constants defined within tile_lib.h
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# Channel ID (CID) for TOA connectionless channel defined in toa.h:104
TOA_CONNECTIONLESS_CID = b"\x00"

class Toa_Cmd_Code(Enum):
    TOFU_CTL      = b"\x01"
    TOFU_DATA     = b"\x02"
    BDADDR        = b"\x03"
    TDT           = b"\x04" 
    SONG          = b"\x05" 
    PPM           = b"\x06" 
    ADV_INT       = b"\x07"
    TKA           = b"\x08"
    TAC           = b"\x09" 
    TDG           = b"\x0a" 
    TMD           = b"\x0b" 
    TCU           = b"\x0c" 
    TIME          = b"\x0d" 
    TEST          = b"\x0e" 
    TFC           = b"\x0f" 
    OPEN_CHANNEL  = b"\x10"
    CLOSE_CHANNEL = b"\x11"
    READY         = b"\x12"
    TDI           = b"\x13" 
    AUTHENTICATE  = b"\x14"
    TMF           = b"\x15" 
    TLIL          = b"\x16" 
    TEF           = b"\x17"
    TRM           = b"\x18"
    TPC           = b"\x19"
    ASSOCIATE     = b"\x1A"

class Toa_Rsp_Code(Enum):
    RESERVED      = b"\x00"
    READY         = b"\x01"
    TOFU_CTL      = b"\x02"
    ASSERT        = b"\x03"
    BDADDR        = b"\x04"
    ERROR         = b"\x05"
    TDT           = b"\x06"
    SONG          = b"\x07"
    PPM           = b"\x08"
    ADV_INT       = b"\x09"
    TKA           = b"\x0A"
    TAC           = b"\x0B"
    TDG           = b"\x0C"
    TMD           = b"\x0D"
    TCU           = b"\x0E"
    TIME          = b"\x0F"
    TEST          = b"\x10"
    TFC           = b"\x11"
    OPEN_CHANNEL  = b"\x12"
    CLOSE_CHANNEL = b"\x13"
    TDI           = b"\x14"
    AUTHENTICATE  = b"\x15"
    TMF           = b"\x16"
    TLIL          = b"\x17"
    TEF           = b"\x18"
    TRM           = b"\x19"
    TPC           = b"\x1A"
    ASSOCIATE     = b"\x1B"
    AUTHORIZED    = b"\x1C"

# Send connectionless cmd -- necessary for channel setup and TDI commands; doesn't require auth key
async def send_connectionless_cmd(tile: 'Tile', cmd_code: Toa_Cmd_Code, payload: bytes) -> bytes:
  data: bytes = TOA_CONNECTIONLESS_CID + tile.token + cmd_code.value + payload
  if debug : print(f"Adding {data.hex()} to the send_queue")
  await tile.send_queue.put(data)

MAX_PAYLOAD_LEN = 22

def get_mic_hash(session_key, nonce, direction, plaintext):
  plaintext_len = len(plaintext).to_bytes(1, "little")
  fixed_padding = b"\x00" * 4
  variable_padding = (MAX_PAYLOAD_LEN - len(plaintext)) * b"\x00"
  msg = nonce + fixed_padding + direction + plaintext_len + plaintext + variable_padding
  return hmac.new(session_key, msg=msg, digestmod=sha256).digest()[:4]

# Send channel cmd -- necessary for just about everything else, authenticated w/ auth key
async def send_channel_cmd(tile: 'Tile', cmd_code: Toa_Cmd_Code, payload: bytes) -> bytes:
  await tile._session_key_created_evt.wait()

  plaintext = cmd_code.value + payload
  tile.nonce_a += 1
  mic = get_mic_hash(tile.session_key, tile.nonce_a.to_bytes(4, "little"), b"\x01", plaintext)
  final_payload = tile.channel_id + plaintext + mic

  if debug : print(f"Adding {final_payload.hex()} to the send_queue")
  await tile.send_queue.put(final_payload)

async def rsp_handler(tile: 'Tile', _sender: int, data: bytearray):
    rsp_data = bytes(data)
    if debug : print(f"Received: {rsp_data.hex()}")
    if rsp_data[0:1] == TOA_CONNECTIONLESS_CID:
        token = rsp_data[1:5]
        rsp_code = rsp_data[5:6]
        rsp_payload = rsp_data[6:]

        if rsp_code == Toa_Rsp_Code.OPEN_CHANNEL.value:
            from commands.channel import handle_open_channel_rsp
            handle_open_channel_rsp(tile, rsp_payload)
        elif rsp_code == Toa_Rsp_Code.TDI.value:
            from commands.tdi import handle_tdi_rsp
            handle_tdi_rsp(tile, rsp_payload)
        else:
            print(f"unhandled rsp_code: {rsp_code}")
    else:
      rsp_code = rsp_data[1:2]
      rsp_payload = rsp_data[2:]
      if rsp_code == Toa_Rsp_Code.TOFU_CTL.value:
        from commands.tofu import handle_tofu_ctl_rsp
        handle_tofu_ctl_rsp(tile, rsp_payload)
      elif rsp_code == Toa_Rsp_Code.TKA.value:
        from commands.tka import handle_tka_rsp
        await handle_tka_rsp(tile, rsp_payload)
      elif rsp_code == Toa_Rsp_Code.SONG.value:
        from commands.song import handle_song_rsp
        handle_song_rsp(tile, rsp_payload)
      else:
        print("received unhandled response")

def disconnected_callback(client):
    print("Client with address {} got disconnected!".format(client.address))

# cmd_sender thread loop; waits for commands to be placed on the send_queue
async def cmd_sender(tile: 'Tile'):
  while True:
    try:
      print(f"Attempting to connect to Tile device @ {tile.mac_address}")
      async with bleak.BleakClient(tile.mac_address, timeout=15) as client:
        print(f"Successfully connected to {tile.mac_address}")
        client.set_disconnected_callback(disconnected_callback)
        await client.start_notify(TILE_TOA_RSP_UUID, partial(rsp_handler, tile))
        while True:
          if tile.send_queue.empty() and tile._thread_ended:
            if debug : print("will break now and close the threads")
            return
          data: bytes = await tile.send_queue.get()
          if debug : print(f"Attempting to send {data.hex()} to {tile.mac_address}")
          await client.write_gatt_char(TILE_TOA_CMD_UUID, data)
    except Exception as e:
      print(e)
