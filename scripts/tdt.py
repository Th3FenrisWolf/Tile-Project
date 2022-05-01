import sys, os
from time import sleep
from known_tiles import Known_Tiles
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile_api'))

# To make commonly used classes easy to import (without duplicating them), import them in tile/__init__.py
# If tile/__init__.py has "from commands.ring import Songs" in it, I can do "from tile import Songs" here,
# otherwise I'd have to do "from tile.commands.ring import Songs" here
from tile import Tile, Songs, Strength

id       = Known_Tiles.backpack_id.value
auth_key = Known_Tiles.backpack_auth.value

# Auth key is only necessary if the commands we want to send require it, otherwise it can be excluded
tile = Tile(id, auth_key)

# Connect if the tile isn't connected, open a channel if there isn't already one open, and send the ring command
tile.ring(Songs.FIND.value, Strength.LOW.value)

def action():
    import vlc
    import pafy
    import time

    media = vlc.MediaPlayer("/home/tile/Downloads/gotcha.mp4")
    media.set_fullscreen(True)
    media.play()

while True:
    tile.wait_for_single_tap()
    action()
