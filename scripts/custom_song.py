import sys, os
from known_tps import Known_Tps
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))
from tile import Tile, Songs, Strength
from known_tiles import Known_Tiles
from time import sleep

tile = Tile("db:1a:96:20:d0:a0", Known_Tiles.toy_auth.value)

tile.ring(Songs.FIND.value, Strength.LOW.value)

sleep(10)

tile.send_custom_song(Known_Tps.skipping_stones.value)

sleep(10)

tile.ring(Songs.FIND.value, Strength.LOW.value)

tile.disconnect()