
from functools import cached_property
from hashlib import sha256
from queue import Queue
import asyncio
from re import A
import threading
from time import sleep
from toa import cmd_sender, send_channel_cmd
from commands.channel import request_open_channel
from commands.tdi import *
from commands.song import request_ring_and_wait_response, request_song_program, upload_custom_song, Strength, Songs
from os import path
from commands.tofu import request_tofu_ready, upload_firmware
from get_mac_address import get_mac_address

# random byte values, required as seen used in the assembly 
sres = b"\x22" * 4

class Tile:

    # https://stackoverflow.com/questions/63858511/using-threads-in-combination-with-asyncio
    def _start_async(self):
        self._loop  = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever)
        self._loop_thread.start()

    def submit_async(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable, self._loop)

    def __init__(self, tile_id: str, auth_key: bytes = None):

        self._start_async()

        self._thread_ended = False

        self._cmd_sender_ended = False
        
        self.auth_key = auth_key

        async def _get_mac_address(self, tile_id):
            mac = await get_mac_address(tile_id)
            if mac:
                self.mac_address = mac
            else:
                # no mac address found, throw exception
                raise Exception("No MAC address found for given Tile ID")
            
        self.submit_async(_get_mac_address(self, tile_id)).result()

        async def set_queue(self):
            self.send_queue = asyncio.Queue()
        self.submit_async(set_queue(self)).result()

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
        else:
            self._thread_ended = True

         # coroutine that runs forever
        self._cmd_sender_future = self.submit_async(cmd_sender(self))

        # wait for open channel to complete before returning
        if self.auth_key is not None:
            async def wait_open_channel(self):
                await self._session_key_created_evt.wait()
            self.submit_async(wait_open_channel(self)).result()

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

    @property
    def curr_song_id(self) -> int:
        async def _create_song_map_rsp_evt(self):
            self._song_map_rsp_evt = asyncio.Event()    

        # create async event if it does not exist or clear it
        if hasattr(self, '_song_map_rsp_evt'):
            self._song_map_rsp_evt.clear()
        else:
            self.submit_async(_create_song_map_rsp_evt(self))
        
        # request song id
        from commands.song import request_read_song_map
        self.submit_async(request_read_song_map(self))

        # wait for response
        async def _wait_for_song_map_rsp(self):
            await self._song_map_rsp_evt.wait()
        
        self.submit_async(_wait_for_song_map_rsp(self)).result()

        return self._curr_song_id

    # NOTE: This function should essentially pass everything along to ring.py, where it actually sends the command.
    #       This functionality, however, does need to be accessible via calling Tile.ring according to CCSW
    def ring(self, song_number: bytes, strength: bytes = Strength.MEDIUM.value):
        self.submit_async(request_ring_and_wait_response(self, song_number, strength)).result()

    def send_firmware_update(self, file_path: str, firmware_version: str):

        async def _create_tofu_ctl_resume_ready_rsp_evt(self):
            self._tofu_ctl_resume_ready_rsp_evt = asyncio.Event()

        async def _create_tofu_ctl_block_ready_rsp_evt(self):
            self._tofu_ctl_block_ready_rsp_evt = asyncio.Event()

        self.submit_async(_create_tofu_ctl_resume_ready_rsp_evt(self)).result()
        self.submit_async(_create_tofu_ctl_block_ready_rsp_evt(self)).result()

        file_size = path.getsize(file_path)
        
        # send tofu ctl ready
        self.submit_async(request_tofu_ready(self, firmware_version, file_size)).result()

        # start sending data 
        self.submit_async(upload_firmware(self, file_path)).result()

    def send_custom_song(self, file_path: str):
        
        async def _create_song_program_ready_rsp_evt(self):
            self._song_program_ready_rsp_evt = asyncio.Event()

        async def _create_song_block_ok_rsp_evt(self):
            self._song_block_ok_rsp_evt = asyncio.Event()

        self.submit_async(_create_song_program_ready_rsp_evt(self)).result()
        self.submit_async(_create_song_block_ok_rsp_evt(self)).result()

        # verify that song is not already currently programmed song
        with open(file_path, 'rb') as f:
            # looking at song_hdr_info_t struct, offset 2 is a uint16_t that is the song_id
            file_song_id = int.from_bytes(f.read(4)[2:4], 'little')
            if self.curr_song_id == file_song_id:
                return

        file_size = path.getsize(file_path)

        # send song program
        self.submit_async(request_song_program(self, file_size)).result()

        # start sending data
        self.submit_async(upload_custom_song(self, file_path)).result()



    def disconnect(self):
        # close channel if channel has been established
        if self.auth_key is not None:
            self.submit_async(send_channel_cmd(self, Toa_Cmd_Code.CLOSE_CHANNEL, b"")).result()
            # shut down the thread
            #print("thread_ended setting to true")
            self._thread_ended = True

        #print("waiting for cmd_sender to end")
        self._cmd_sender_future.result()

        self._loop.call_soon_threadsafe(self._loop.stop)

        # necessary sleep, so that loop stops before closing
        sleep(0.1)

        self._loop.call_soon_threadsafe(self._loop.close)

        #print("Waiting for thread")
        self._loop_thread.join()

        print("Tile Channel closed -- Disconnected")
