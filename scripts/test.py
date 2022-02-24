import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))
from tile_api import Tile
from known_tiles import Known_Tiles

tile = Tile(Known_Tiles.spare_key_mac.value)  # TDI command doesn't require a channel, so auth key isn't needed

print(f"TileID {tile.tile_id}")
print(f"TileID {tile.tile_id}")
print(f"TileID {tile.tile_id}")