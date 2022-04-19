import asyncio
from re import search
from bleak import BleakScanner, BleakClient
from functools import partial
from commands.tdi import Tdi_Cmd_Code, Tdi_Rsp_Code
from toa import Toa_Cmd_Code, Toa_Rsp_Code
import itertools

# Print Debug info
debug = True

# only connections with an RSSI better than this will be attempted
RSSI_SEARCH_THRESHOLD = -75

# connector wait time (in seconds) before processing PQ of devices found
# (This ensures that we do not try to talk to a device with a bad connection first) --
#   essentially wait for some devices with a good connection strength to appear in the queue
DELAY_START = 10

# for bleak connnection
# max number of times the connector will try to get the tile ID from the tile
MAX_CONNECTION_ATTEMPTS = 3
CONNECTION_TIMEOUT = 30 # number of seconds per connection attempt before retrying

# UUIDs unique to Tile to identify sent and received commands
TILE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"

# Constants for retrieving the Tile ID from a device
TOKEN = b"\x00" * 4
TOA_CONNECTIONLESS_CID = b"\x00"
TDI_GET_TILE_ID_CMD_PAYLOAD = TOA_CONNECTIONLESS_CID + TOKEN + Toa_Cmd_Code.TDI.value + Tdi_Cmd_Code.tile_id.value

# unique sequence count
counter = itertools.count()

class Tile_ID_Wrapper:
    def __init__(self, got_tile_id_evt):
        self.got_tile_id_evt = got_tile_id_evt
        
def tile_id_rsp_handler(tile_id_wrapper, _sender, data):
    rsp_data = bytes(data)
    if rsp_data[0:1] == TOA_CONNECTIONLESS_CID:
        rsp_code = rsp_data[5:6]
        rsp_payload = rsp_data[6:]
        if rsp_code == Toa_Rsp_Code.TDI.value:
            tdi_rsp_code = rsp_payload[0:1]
            if tdi_rsp_code == Tdi_Rsp_Code.tile_id.value:
                tile_id_wrapper.tile_id = rsp_payload[1:].hex()
                tile_id_wrapper.got_tile_id_evt.set()

class Scan_Conditions:
    def __init__(self) -> None:
        self.scanning = True
        self.found_tile_mac = ""

async def get_tile_id(mac_address):
    for _ in range(MAX_CONNECTION_ATTEMPTS):
        try:
            async with BleakClient(mac_address, timeout=CONNECTION_TIMEOUT) as client:
                tile_id_wrapper = Tile_ID_Wrapper(asyncio.Event())
                await client.start_notify(TILE_TOA_RSP_UUID, partial(tile_id_rsp_handler, tile_id_wrapper))
                await client.write_gatt_char(TILE_TOA_CMD_UUID, TDI_GET_TILE_ID_CMD_PAYLOAD)
                await tile_id_wrapper.got_tile_id_evt.wait()
                return tile_id_wrapper.tile_id
        except Exception:
            pass

async def detection_callback(discovered_tiles_pq, device, advertisement_data):
    # check the found device to see if it is a tile
    # make sure it has service data before dereferencing service data
    if hasattr(advertisement_data, 'service_data') and TILE_UUID in str(advertisement_data.service_data):
        # we found a tile
        # create empty set found_addr_set if not yet created
        if not hasattr(detection_callback, "found_addr_set"):
            detection_callback.found_addr_set = set()
        if device.address not in detection_callback.found_addr_set:
            # document only unique instances
            detection_callback.found_addr_set.add(device.address)
            # place the device on the discovered tiles processing queue for the connector to use
            await discovered_tiles_pq.put((device.rssi, next(counter), device))

async def connector(discovered_tiles_pq, search_id, scan_conditions):
    # wait some time before connecting to make sure that we don't try to talk to the weaker connections first
    await asyncio.sleep(DELAY_START)

    while True: 
        # stop processing the discovered_tiles_pq if
        # 1. We found a tile with the desired tile_id
        # 2. The queue is empty and the scanner is finished (we never found it))
        if scan_conditions.found_tile_mac or (not scan_conditions.scanning and discovered_tiles_pq.empty()):
            return
        # pull device off the queue
        device = (await discovered_tiles_pq.get())[-1]
        # Determine whether Tile is in range
        if int(device.rssi) > RSSI_SEARCH_THRESHOLD: 
            # if in range, get the Tile ID
            tile_id = await get_tile_id(device)
            
            # check if tile of interest found
            if tile_id == search_id:
                scan_conditions.found_tile_mac = device.address

async def get_mac_address(search_id, search_time = 80) -> str:
    # force search_id to be lowercase
    search_id = search_id.lower()

    scan_conditions = Scan_Conditions()

    # this pq contains tile devices to check their tile id, priority is based on RSSI (connection strength)
    discovered_tiles_pq = asyncio.PriorityQueue()
    # set up the connector task
    connector_future = asyncio.create_task(connector(discovered_tiles_pq, search_id, scan_conditions))
    # register the scanner and callback function
    scanner = BleakScanner()
    scanner.register_detection_callback(partial(detection_callback, discovered_tiles_pq))
    # run scanner
    await scanner.start()
    # better way to do this: https://stackoverflow.com/questions/37209864/interrupt-all-asyncio-sleep-currently-executing
    for _ in range(search_time):
        await asyncio.sleep(1)
        if scan_conditions.found_tile_mac:
            break
    else:
        # TODO throw exception
        scan_conditions.found_tile_mac = None
        print("ERROR never found mac address for given tile id")
    await scanner.stop()
    if debug: print("scanner stopped, awaiting connector thread shutdown")
    scan_conditions.scanning = False
    # wait for the connector task to end before closing
    await connector_future
    return scan_conditions.found_tile_mac

# Code below was used for debugging purposes and may still be useful for future research
import time
if __name__ == '__main__':
    try:
        start = time.time()
        print(asyncio.run(get_mac_address("615BA301A0F17F22")))
        end = time.time()
        print(f"({str(end - start)[:4]} seconds)")
    except KeyboardInterrupt:
        print("\nScanner terminated early")