import sys
sys.path.append("/home/tile/Desktop/cedarville-2021/tile")
from tile import Tile

spare_key_mac = "E6:9E:55:1A:91:28"
backpack_mac = "E1:5B:A3:01:A0:F1"
toy_mac = "D1:7F:8E:E6:9E:B1"

tile = Tile(spare_key_mac)  # TDI command doesn't require a channel, so auth key isn't needed

# See @property decorator, store results so future references to properties that have 
# already been used don't send unnecessary commands
print(f"Tile {tile.tile_id} is model {tile.model_num} running firmware {tile.fw_version}")

# This shouldn't send another TDI command
print(f"Tile {tile.tile_id}")