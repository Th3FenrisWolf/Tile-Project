from queue import Queue
from toa import Toa_Cmd_Code, send_connectionless_cmd
import asyncio
import hmac
from hashlib import sha256


# CMD

async def request_open_channel(tile: 'Tile') -> None:
    await send_connectionless_cmd(tile, Toa_Cmd_Code.OPEN_CHANNEL, tile.rand_a)

# RSP

def handle_open_channel_rsp(tile: 'Tile', rsp_payload: bytes):
    tile.nonce_a = 0
    tile.nonce_t = 0
    tile.channel_id = rsp_payload[0:1]
    rand_t = rsp_payload[1:]
    tile.session_key = create_session_key(tile.auth_key, tile.rand_a, rand_t, tile.channel_id, tile.token)
    tile._session_key_created_evt.set()

# UTIL

def create_session_key(auth_key: bytes, rand_a: bytes, rand_t: bytes, channel_id: bytes, token: bytes) -> bytes:
    message = rand_a + rand_t + channel_id + token
    # only uses 16 bytes (or half of the hmac)
    session_key = hmac.new(auth_key, msg=message, digestmod = sha256).digest()[:16]
    return session_key