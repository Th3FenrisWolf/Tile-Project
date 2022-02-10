import sys, os
from known_tiles import Known_Tiles
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tile'))

# To make commonly used classes easy to import (without duplicating them), import them in tile/__init__.py
# If tile/__init__.py has "from commands.ring import Songs" in it, I can do "from tile import Songs" here,
# otherwise I'd have to do "from tile.commands.ring import Songs" here
from tile import Tile, Songs

mac      = Known_Tiles.spare_key_mac.value
auth_key = Known_Tiles.spare_key_auth.value

# Auth key is only necessary if the commands we want to send require it, otherwise it can be excluded
tile = Tile(mac, auth_key)
# Connect if the tile isn't connected, open a channel if there isn't already one open, and send the ring command
tile.ring(Songs.WAKEUP.value)
