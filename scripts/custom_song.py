import sys, os
from known_tps import Known_Tps
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile_api'))
from tile import Tile, Songs, Strength
from known_tiles import Known_Tiles
from time import sleep

tile = Tile(Known_Tiles.toy_id.value, Known_Tiles.toy_auth.value)

tile.ring(Songs.FIND.value, Strength.LOW.value)

print(tile.curr_song_id)

sleep(15)

tile.send_custom_song(Known_Tps.to_and_fro.value)

sleep(15)

print(tile.curr_song_id)

tile.ring(Songs.FIND.value, Strength.LOW.value)

tile.disconnect()