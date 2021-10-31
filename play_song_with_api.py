import asyncio
from tile_api import Tile
import time

mac_address = "e6:9e:55:1a:91:28"

async def main(): 
    myTile = await Tile.create(mac_address)
    await myTile.open_channel()
    await myTile.play_song()

asyncio.run(main())