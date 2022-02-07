import sys
sys.path.append("/home/tile/Desktop/cedarville-2021/tile")

spare_key_mac = "E6:9E:55:1A:91:28"
spare_key_auth = b"\x59\xBE\xCA\x33\xAC\x3D\x4A\x65\xC7\x1E\xEB\xCA\x8D\x91\x8B\x77"
backpack_mac = "E1:5B:A3:01:A0:F1"
backpack_auth = b"\x59\xAC\x89\xEB\x6A\xF6\x80\xD0\x05\xFE\x8F\x8B\xCD\x9C\x85\x2F"
toy_mac = "D1:7F:8E:E6:9E:B1"

# To make commonly used classes easy to import (without duplicating them), import them in tile/__init__.py
# If tile/__init__.py has "from commands.ring import Songs" in it, I can do "from tile import Songs" here,
# otherwise I'd have to do "from tile.commands.ring import Songs" here
from tile import Tile, Songs

# Auth key is only necessary if the commands we want to send require it, otherwise it can be excluded
tile = Tile(spare_key_mac, spare_key_auth)
# Connect if the tile isn't connected, open a channel if there isn't already one open, and send the ring command
tile.ring(Songs.FIND.value)
