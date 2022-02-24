import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))
from tile_api import Tile
from known_tiles import Known_Tiles

tile = Tile("ff:bd:9c:b1:c2:5f")  # TDI command doesn't require a channel, so auth key isn't needed

# See @property decorator, store results so future references to properties that have 
# already been used don't send unnecessary commands
print(f"Tile {tile.tile_id} is model {tile.model_num} running firmware {tile.fw_version}")

# This shouldn't send another TDI command
print(f"Tile {tile.tile_id}")

tile.disconnect()