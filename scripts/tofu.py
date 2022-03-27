import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile_api'))
from tile import Tile
from known_tiles import Known_Tiles

tile = Tile(Known_Tiles.backpack_id.value, Known_Tiles.backpack_auth.value)

file_path = "/home/tile/Desktop/cedarville-2021/tile_firmwares/Tile_FW_Image_25.04.06.0.bin"

tile.send_firmware_update(file_path, "25.04.06.0")

tile.disconnect()