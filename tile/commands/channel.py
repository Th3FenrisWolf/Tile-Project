from toa import Toa_Cmd_Code, send_connectionless_cmd
import asyncio

def open_channel(mac_address: str, rand_a: bytes) -> bytes:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(send_connectionless_cmd(mac_address, Toa_Cmd_Code.OPEN_CHANNEL, rand_a))