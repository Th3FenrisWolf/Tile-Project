import asyncio
from tile_api import Tile
import time

# specifc to our tile, acquired from ble scanning and verified in disassembly
MAC_ADDRESS = "e6:9e:55:1a:91:28"

# specifc to our tile, in disassembly from toa_module struct
AUTH_KEY = b"\x59\xbe\xca\x33\xac\x3d\x4a\x65\xc7\x1e\xeb\xca\x8d\x91\x8b\x77"

async def main(): 
    myTile = await Tile.create(MAC_ADDRESS, AUTH_KEY)
    await myTile.open_channel()
    await myTile.play_song()

asyncio.run(main())