import asyncio
from bleak import BleakClient
from bleak import BleakScanner
from functools import cached_property
import bleak

import hmac
import hashlib

from commands.tdi import *
from tile.commands.channel import open_channel

# random byte values, required as seen used in the assembly 
sres = b"\x22" * 4

class Tile:
    def __init__(self, mac_address: str, auth_key: bytes = None):
        self.auth_key = auth_key
        # bleak seems to require uppercase str, so this will catch if someone gave lowercase form
        self.mac_address = mac_address.upper()

    @cached_property
    def tile_id(self) -> str:
        return get_tile_id(self.mac_address)

    @cached_property
    def fw_version(self) -> str:
        return get_fw_version(self.mac_address)

    @cached_property
    def model_num(self) -> str:
        return get_model_num(self.mac_address)

    @cached_property
    def hw_version(self) -> str:
        return get_hw_version(self.mac_address)

    @staticmethod
    def create_session_key(auth_key: bytes, allocated_cid: bytes, rand_a: bytes, rand_t: bytes):
        message = rand_a + rand_t + allocated_cid + sres
        # only uses 16 bytes (or half of the hmac)
        session_key = hmac.new(auth_key, msg=message, digestmod = hashlib.sha256).digest()[:16]
        return session_key

    def aquire_channel(self):
        assert self.auth_key is not None, "Auth key required to issue channel command"

        # random byte values, required random byte as found in toa.h:295 
        rand_a = b"\x00" * 14

        # found in toa.h:190
        rsp_data = open_channel(self.mac_address, rand_a)
        self.allocated_cid = rsp_data[6:7]
        rand_t = rsp_data[7:]
        self.session_key = Tile.create_session_key(self.auth_key, self.allocated_cid, rand_a, rand_t)
