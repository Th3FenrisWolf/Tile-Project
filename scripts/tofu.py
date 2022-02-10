import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))
from tile import Tile
from known_tiles import Known_Tiles

tile = Tile(Known_Tiles.backpack_mac.value, Known_Tiles.backpack_auth.value)

tile.update(firmware_version)
