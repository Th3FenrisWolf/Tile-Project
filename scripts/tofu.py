import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))
from tile_api import Tile
from known_tiles import Known_Tiles

tile = Tile(Known_Tiles.backpack_mac.value, Known_Tiles.backpack_auth.value)

file_path = "/home/tile/Downloads/Tile_FW_Image_25.03.29.0.bin"

tile.send_firmware_update(file_path, "25.03.29.0")

tile.disconnect()