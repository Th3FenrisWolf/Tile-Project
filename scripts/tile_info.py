import sys, os, asyncio
from known_tiles import Known_Tiles
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile_api'))
from tile import Tile
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'discover_scripts'))
from list_nearby_tiles import get_tile_id

# If TileID is unknown, you may use list_nearby_tiles.get_tile_id(bt_addr)
# bt_addr = "E1:5B:A3:01:A0:F1"6
# tile_id = asyncio.run(get_tile_id(bt_addr))

tile = Tile(Known_Tiles.backpack_id.value)  # TDI command doesn't require a channel, so auth key isn't needed

# See @property decorator, store results so future references to properties that have 
# already been used don't send unnecessary commands
print(f"Tile {tile.tile_id} is model {tile.model_num} running firmware {tile.fw_version}")

# This shouldn't send another TDI command
print(f"Tile {tile.tile_id}")

tile.disconnect()