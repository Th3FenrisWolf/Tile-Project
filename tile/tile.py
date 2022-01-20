import asyncio
from sqlite3 import connect
from bleak import BleakClient
from bleak import BleakScanner
from functools import cached_property
import bleak

import hmac
import hashlib

from commands.tdi import *

# random byte values, required random byte as found in toa.h:295 
rand_a = b"\x00" * 14

# random byte values, required as seen used in the assembly 
sres = b"\x22" * 4

class Tile:

    client = None
    session_key = None
    allocated_cid = None
    done = False

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

    # todo move / hide method
    async def findTile(self, mac_address: str):
        while True:
            print('Searching For Tile...')
            async with BleakScanner() as scanner:
                await asyncio.sleep(5.0)
                for d in scanner.discovered_devices:
                    if d.address == mac_address:
                        print("Tile Found!")
                        return BleakClient(d)
    
    # todo move / hide method
    async def connectTile(self):
        #connect using Bleak API's connect; attempt to catch exceptions
        while True:
            print('Connecting To Tile...')
            try:
                await self.client.connect(timeout = 30)
                print("Successfully Connected To Tile")
                return
            except asyncio.exceptions.TimeoutError as e:
                print('AsyncIO Timed Out, Trying Again')
            except bleak.exc.BleakError as e:
                print('Fatal Bleak Error, See Below:')
                print(f'\t{e}')
                exit()
            except Exception as e:
                print('Unexpected Error, See Below:')
                print(f'\t{e}')
                exit()
            finally:
                await self.client.disconnect()

    def __init__(self, mac_address: str, auth_key: bytes = None):
        self.auth_key = auth_key

        # bleak seems to require uppercase str, so this will catch if someone gave lowercase form
        self.mac_address = mac_address.upper()

        #loop = asyncio.get_event_loop()
        #self.client = loop.run_until_complete(self.findTile(self.mac_address))

        #loop.run_until_complete(self.connectTile())

    @staticmethod
    def create_session_key(auth_key: bytes, allocated_cid: bytes, rand_t: bytes):
        message = rand_a + rand_t + allocated_cid + sres
        # only uses 16 bytes (or half of the hmac)
        session_key = hmac.new(auth_key, msg=message, digestmod = hashlib.sha256).digest()[:16]
        return session_key

    async def open_channel_rsp_callback(self, sender: int, data: bytearray) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"

        # found in toa.h:190
        # extract data into variables for creating session key
        
        # TODO verify this RSP code is the one we expect by adding assertion
        toa_rsp = data[5:6]
        self.allocated_cid = data[6:7]
        rand_t = data[7:]

        self.session_key = Tile.create_session_key(self.auth_key, self.allocated_cid, rand_t)

        self.done = True

    async def open_channel(self) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"

        # set up callback handle for TOA open channel RSP
        await self.client.start_notify(TILE_TOA_RSP_UUID, self.open_channel_rsp_callback)

        # set parameters for TOA open channel CMD
        cid = TOA_CONNECTIONLESS_CID.to_bytes(1, byteorder='big')
        toa_cmd = Toa_Cmd_Code.OPEN_CHANNEL.to_bytes(1, byteorder='big')

        # issue TOA open channel CMD
        await self.client.write_gatt_char(TILE_TOA_CMD_UUID, cid + sres + toa_cmd + rand_a)

        # wait until callback executed
        while not self.done:
            await asyncio.sleep(0.01)
        self.done = False

        # remove callback handler
        await self.client.stop_notify(TILE_TOA_RSP_UUID)

    # the implicit duration is 0xfe, which appears to just play the song in its entirety
    # strength ranges from 0-3, where 0 is silent and 3 is loudest
    # according to tile_song_module.h:214
    async def play_song(self, number: int, strength: int) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"
        # check that session_key has been set
        assert self.session_key is not None, "Channel must be opened, call open_channel_rsp_callback before this method"
        # check that allocated_cid has been set
        assert self.allocated_cid is not None, "Channel must be opened, call open_channel_rsp_callback before this method"

        # assert correct input parameters
        assert 0 <= strength <= 3, "Strength must have a value in the range of 0-3"

        # first byte is the command
        toa_cmd_code = Toa_Cmd_Code.SONG.to_bytes(1, byteorder='big')
        
        # second byte is the number
        numberByte = number.to_bytes(1, byteorder='big')
        
        # third byte is the strength
        strengthByte = strength.to_bytes(1, byteorder='big')

        toa_cmd_payload = b"\x02" + numberByte + strengthByte
        # necessary for MIC calculations
        MAX_PAYLOAD_LEN = 22
        toa_cmd_code_and_payload_len = (len(toa_cmd_code) + len(toa_cmd_payload)).to_bytes(1, byteorder='big')
        toa_cmd_padding = (MAX_PAYLOAD_LEN - len(toa_cmd_code) - len(toa_cmd_payload)) * b"\0"
        new_message = b"\x01" + b"\x00" * 7 + b"\x01" + toa_cmd_code_and_payload_len + toa_cmd_code + toa_cmd_payload + toa_cmd_padding 
        mic = hmac.new(self.session_key, msg=new_message, digestmod = hashlib.sha256).digest()[:4]
        play_song = self.allocated_cid + toa_cmd_code + toa_cmd_payload + mic

        await self.client.write_gatt_char(TILE_TOA_CMD_UUID, play_song)

# asyncio.run(main(address))