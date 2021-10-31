import asyncio
from bleak import BleakClient

import hmac
import hashlib

# specifc to our tile, acquired from ble scanning and verified in disassembly
address = "e6:9e:55:1a:91:28"

# constants defined within tile_lib.h
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# CID for TOA connectionless channel defined in toa.h:104
TOA_CONNECTIONLESS_CID = 0

# specifc to our tile, in disassembly from toa_module struct
AUTH_KEY = b"\x59\xbe\xca\x33\xac\x3d\x4a\x65\xc7\x1e\xeb\xca\x8d\x91\x8b\x77"

# random byte values, required random byte as found in toa.h:295 
rand_a = b"\x00" * 14

# random byte values, required as seen in the assembly 
sres = b"\x22" * 4

class Toa_Cmd_Code:
  TOA_CMD_TOFU_CTL      = 0x01
  TOA_CMD_TOFU_DATA     = 0x02
  TOA_CMD_BDADDR        = 0x03
  TOA_CMD_TDT           = 0x04 
  TOA_CMD_SONG          = 0x05 
  TOA_CMD_PPM           = 0x06 
  TOA_CMD_ADV_INT       = 0x07
  TOA_CMD_TKA           = 0x08
  TOA_CMD_TAC           = 0x09 
  TOA_CMD_TDG           = 0x0a 
  TOA_CMD_TMD           = 0x0b 
  TOA_CMD_TCU           = 0x0c 
  TOA_CMD_TIME          = 0x0d 
  TOA_CMD_TEST          = 0x0e 
  TOA_CMD_TFC           = 0x0f 
  TOA_CMD_OPEN_CHANNEL  = 0x10
  TOA_CMD_CLOSE_CHANNEL = 0x11
  TOA_CMD_READY         = 0x12
  TOA_CMD_TDI           = 0x13 
  TOA_CMD_AUTHENTICATE  = 0x14
  TOA_CMD_TMF           = 0x15 
  TOA_CMD_TLIL          = 0x16 
  TOA_CMD_TEF           = 0x17
  TOA_CMD_TRM           = 0x18
  TOA_CMD_TPC           = 0x19
  TOA_CMD_ASSOCIATE     = 0x1A

class Tile:

    client = None
    session_key = None
    allocated_cid = None
    done = False

    @classmethod
    async def create(self, mac_address: str):
        self = Tile()
        self.client = BleakClient(mac_address)
        await self.client.connect()
        return self

    async def open_channel_rsp_callback(self, sender: int, data: bytearray) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"

        # found in toa.h:190
        # extract data into variables for creating session key
        toa_rsp = data[5:6]
        self.allocated_cid = data[6:7]
        rand_t = data[7:]
        message = rand_a + rand_t + self.allocated_cid + sres
        # only uses 16 bytes (or half of the hmac)
        self.session_key = hmac.new(AUTH_KEY, msg=message, digestmod = hashlib.sha256).digest()[:16]
        self.done = True

    async def open_channel(self) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"

        # set up callback handle for TOA open channel RSP
        await self.client.start_notify(TILE_TOA_RSP_UUID, self.open_channel_rsp_callback)

        # set parameters for TOA open channel CMD
        cid = TOA_CONNECTIONLESS_CID.to_bytes(1, byteorder='big')
        toa_cmd = Toa_Cmd_Code.TOA_CMD_OPEN_CHANNEL.to_bytes(1, byteorder='big')

        # issue TOA open channel CMD
        await self.client.write_gatt_char(TILE_TOA_CMD_UUID, cid + sres + toa_cmd + rand_a)

        # wait until callback executed, TODO: refactor once you learn how to code
        while not self.done:
            await asyncio.sleep(0.01)
        self.done = False

        # remove callback handler
        await self.client.stop_notify(TILE_TOA_RSP_UUID)

    async def play_song(self) -> None:
        # check that client has been set
        assert self.client is not None, "Client is not set"
        # check that session_key has been set
        assert self.session_key is not None, "Channel must be opened, call open_channel_rsp_callback before this method"
        # check that allocated_cid has been set
        assert self.allocated_cid is not None, "Channel must be opened, call open_channel_rsp_callback before this method"

        # now write
        toa_cmd_code = b"\05"
        # second byte is the number
        # third byte is the strength 
        toa_cmd_payload = b"\x02\04\x01"
        # necessary for mic calculations
        MAX_PAYLOAD_LEN = 22
        toa_cmd_code_and_payload_len = (len(toa_cmd_code) + len(toa_cmd_payload)).to_bytes(1, byteorder='big')
        toa_cmd_padding = (MAX_PAYLOAD_LEN - len(toa_cmd_code) - len(toa_cmd_payload)) * b"\0"
        new_message = b"\x01" + b"\x00" * 7 + b"\x01" + toa_cmd_code_and_payload_len + toa_cmd_code + toa_cmd_payload + toa_cmd_padding 
        mic = hmac.new(self.session_key, msg=new_message, digestmod = hashlib.sha256).digest()[:4]
        play_song = self.allocated_cid + toa_cmd_code + toa_cmd_payload + mic

        await self.client.write_gatt_char(TILE_TOA_CMD_UUID, play_song)

# asyncio.run(main(address))