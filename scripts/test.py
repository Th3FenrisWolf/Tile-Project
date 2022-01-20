import sys
sys.path.append("/home/tile/Desktop/cedarville-2021/tile")
from tile import Tile

tile = Tile("e6:9e:55:1a:91:28")  # TDI command doesn't require a channel, so auth key isn't needed

print(f"TileID {tile.tile_id}")
print(f"TileID {tile.tile_id}")
print(f"TileID {tile.tile_id}")