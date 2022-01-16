# To make commonly used classes easy to import (without duplicating them), import them in tile/__init__.py
# If tile/__init__.py has "from commands.ring import Songs" in it, I can do "from tile import Songs" here,
# otherwise I'd have to do "from tile.commands.ring import Songs" here
from tile import Tile, Songs

# Auth key is only necessary if the commands we want to send require it, otherwise it can be excluded
tile = Tile("<mac address>", "<auth key>")
# Connect if the tile isn't connected, open a channel if there isn't already one open, and send the ring command
tile.ring(Songs.SONG_FIND)
