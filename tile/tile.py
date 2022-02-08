
from functools import cached_property
from hashlib import sha256
from queue import Queue
import asyncio
import threading
from time import sleep
from toa import cmd_sender
from commands.channel import request_open_channel
from commands.tdi import *
from commands.ring import request_ring, Strength, Songs
from os import path
from commands.tofu import request_tofu_ready, upload_firmware

# random byte values, required as seen used in the assembly 
sres = b"\x22" * 4

class Tile:

    # https://stackoverflow.com/questions/63858511/using-threads-in-combination-with-asyncio
    @staticmethod
    def _start_async():
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever).start()
        return loop

    def submit_async(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable, self._loop)

    def __init__(self, mac_address: str, auth_key: bytes = None):

        self._loop = self._start_async()
        
        self.auth_key = auth_key
        # bleak seems to require uppercase str, so this will catch if someone gave lowercase form
        self.mac_address = mac_address.upper()

        async def set_queue(self):
            self.send_queue = asyncio.Queue()
        self.submit_async(set_queue(self)).result()

        # coroutine that runs forever
        self.submit_async(cmd_sender(self))

        # 4 random bytes used in session_key generation
        self.token = b"\x00\x00\x00\x00"

        # automatically get tdi stuff
        async def _create_tdi_rsp_evts(self):
            self._tile_id_rsp_evt = asyncio.Event()
            self._fw_version_rsp_evt = asyncio.Event()
            self._model_num_rsp_evt = asyncio.Event()
            self._hw_version_rsp_evt = asyncio.Event()

        self.submit_async(_create_tdi_rsp_evts(self)).result()
        self.submit_async(request_all_tdi(self)).result()

        if self.auth_key is not None:
            self.rand_a = b"\x00" * 14

            async def _create_session_key_created_evt(self):
                self._session_key_created_evt = asyncio.Event()

            self.submit_async(_create_session_key_created_evt(self)).result()
            self.submit_async(request_open_channel(self)).result()

        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(open_channel(self.send_queue, self.rand_a))

    def __del__(self):
        # stop async loop
        self._loop.call_soon_threadsafe(self._loop.stop)

    @cached_property
    def tile_id(self) -> str:
        async def get_tile_id(self):
            await self._tile_id_rsp_evt.wait()
            return self._tile_id
        return self.submit_async(get_tile_id(self)).result()

    @cached_property
    def fw_version(self) -> str:
        async def get_fw_version(self):
            await self._fw_version_rsp_evt.wait()
            return self._fw_version
        return self.submit_async(get_fw_version(self)).result()

    @cached_property
    def model_num(self) -> str:
        async def get_model_num(self):
            await self._model_num_rsp_evt.wait()
            return self._model_num
        return self.submit_async(get_model_num(self)).result()

    @cached_property
    def hw_version(self) -> str:
        async def get_hw_version(self):
            await self._hw_version_rsp_evt.wait()
            return self._hw_version
        return self.submit_async(get_hw_version(self)).result()


    # NOTE: This function should essentially pass everything along to ring.py, where it actually sends the command.
    #       This functionality, however, does need to be accessible via calling Tile.ring according to CCSW
    def ring(self, song_number: bytes, strength: bytes = Strength.MEDIUM.value):
        self.submit_async(request_ring(self, song_number, strength)).result()

    def send_firmware_update(self, file_path: str, firmware_version: str):

        async def _create_tofu_ctl_resume_ready_rsp_evt(self):
            self._tofu_ctl_resume_ready_rsp_evt = asyncio.Event()

        self.submit_async(_create_tofu_ctl_resume_ready_rsp_evt(self)).result()

        file_size = path.getsize(file_path)
        # send tofu ctl ready
        self.submit_async(request_tofu_ready(self, firmware_version, file_size)).result()
        # wait for response confirmation_block_length

        # start sending data 
        self.submit_async(upload_firmware(self, file_path, file_size)).result()
