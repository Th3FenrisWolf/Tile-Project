import sys
sys.path.append("/home/tile/Desktop/cedarville-2021/tile")

# To make commonly used classes easy to import (without duplicating them), import them in tile/__init__.py
# If tile/__init__.py has "from commands.ring import Songs" in it, I can do "from tile import Songs" here,
# otherwise I'd have to do "from tile.commands.ring import Songs" here
from tile import Tile, Songs

# Auth key is only necessary if the commands we want to send require it, otherwise it can be excluded
tile = Tile("e6:9e:55:1a:91:28", b"\x59\xBE\xCA\x33\xAC\x3D\x4A\x65\xC7\x1E\xEB\xCA\x8D\x91\x8B\x77")
# Connect if the tile isn't connected, open a channel if there isn't already one open, and send the ring command
tile.ring(Songs.FIND.value)
