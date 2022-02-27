import asyncio
from re import search
from bleak import BleakScanner, BleakClient
from enum import Enum
import sys, os
from functools import partial
import threading
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '../tile_api'))
from commands.tdi import Tdi_Cmd_Code, Tdi_Rsp_Code
from toa import Toa_Cmd_Code, Toa_Rsp_Code

known_addresses = {
    # Change this dictionary to your own devices and known MAC addresses as you find them
    "Spare key":            "E6:9E:55:1A:91:28",
    "Wallet":               "DF:30:61:4F:AB:DA",
    "Backpack":             "E1:5B:A3:01:A0:F1",
    "Toy":                  "D1:7F:8E:E6:9E:B1",
    "madelines_earbud1":    "12:34:56:00:33:E1",
    "madelines_earbud2":    "12:34:56:00:37:1D"
}

scanning = True
found_addr_list = []
search_id = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"
tiles_found = 0
found_tile_id = False

# stuff used for getting the Tile ID
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"
token = b"\x00" * 4
TOA_CONNECTIONLESS_CID = b"\x00"
data: bytes = TOA_CONNECTIONLESS_CID + token + Toa_Cmd_Code.TDI.value + Tdi_Cmd_Code.tile_id.value

class Pad_Lengths(Enum):
    DEVICE_NUM = 4
    NAME = 20   # <-- increase this value if you have longer known_device names
    ADDRESS = 19
    RSSI = 25
    TILE_ID = 53

class Formatting(Enum):
    INVERTED = "\u001b[1m"
    BOLD = "\u001b[7m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    RED = "\u001b[31m"
    CLEAR = "\u001b[0m"

class RSSI_Threshold(Enum):
    STRONG = -50
    MODERATE = -70

# function to return key for any value
def get_key(val, dict) -> str:
    for key, value in dict.items():
        if val == value:
            return key
    return None

def pad(string, pad_length):
    padded_string = string
    while len(padded_string) < pad_length :
        padded_string += " "
    return padded_string

def print_header():
    head = Formatting.BOLD.value
    #head += pad("#", Pad_Lengths.DEVICE_NUM.value)
    head += pad("Name", Pad_Lengths.NAME.value)
    head += pad("Address", Pad_Lengths.ADDRESS.value)
    head += pad("Signal Strength", Pad_Lengths.RSSI.value)
    head += pad("Tile ID:", Pad_Lengths.TILE_ID.value)
    print(head + Formatting.CLEAR.value)

async def get_device_data(pq, device, _advertisement_data, tile_id = None, querying = False) -> str:
    info = ""
    global scanning
    global search_id
    global found_tile_id
    #check if device has been processed yet
    if tile_id is None:
        # place the device on the processing queue
        try:
            if search_id is not None and not found_tile_id:
                await pq.put((abs(device.rssi), device))
                return ""
        except Exception as e:
            # occasionally an exception is thrown when putting a device on the queue, but it still works fine
            pass
    #info += pad(str(tiles_found), Pad_Lengths.DEVICE_NUM.value)
    info += pad(device.name, Pad_Lengths.NAME.value)
    info += device.address + "  "
    info += str(device.rssi) + " "
    # Interpret RSSI
    if int(device.rssi) > RSSI_Threshold.STRONG.value:
        info += pad(Formatting.GREEN.value + "Strong" + Formatting.CLEAR.value, Pad_Lengths.RSSI.value)
    elif int(device.rssi) > RSSI_Threshold.MODERATE.value:
        info += pad(Formatting.YELLOW.value + "Moderate" + Formatting.CLEAR.value, Pad_Lengths.RSSI.value)
    else:
        info += pad(Formatting.RED.value + "Weak" + Formatting.CLEAR.value, Pad_Lengths.RSSI.value)
    # prevent null string error for Tile ID
    info += str(tile_id)
    return info

async def detection_callback(pq, device, advertisement_data):
    # Whenever a device is found...
    global search_id
    global found_addr_list
    global tileUUID
    global known_addresses
    global tiles_found
    if hasattr(advertisement_data, 'service_data'):
        if tileUUID in str(advertisement_data.service_data):
            # we found a tile
            if device.address not in found_addr_list:
                # document only unique instances
                found_addr_list.append(device.address)
                if search_id == None:
                    # if not searching for any particular tile:
                    # exclude devices we don't want to appear
                    # if device is known, give it a meaningful name
                    if device.address in known_addresses.values():
                        device.name = get_key(device.address, known_addresses)
                        print(await get_device_data(pq, device, advertisement_data), end="")
                    # otherwise just print
                    else:
                        device.name = "Unknown Tile"
                        print(await get_device_data(pq, device, advertisement_data), end="")
                else:
                    # we are searching for a particular tile
                    print(await get_device_data(pq, device, advertisement_data), end="")

                
class Tile_ID_Wrapper :
    def __init__(self, got_tile_id_evt):
        self.got_tile_id_evt = got_tile_id_evt

def tile_id_rsp_handler(tile_id_wrapper, _sender, data):
    rsp_data = bytes(data)
    if rsp_data[0:1] == TOA_CONNECTIONLESS_CID:
        token = rsp_data[1:5]
        rsp_code = rsp_data[5:6]
        rsp_payload = rsp_data[6:]
        if rsp_code == Toa_Rsp_Code.TDI.value:
            tdi_rsp_code = rsp_payload[0:1]
            if tdi_rsp_code == Tdi_Rsp_Code.tile_id.value:
                tile_id_wrapper.tile_id = rsp_payload[1:].hex()
                tile_id_wrapper.got_tile_id_evt.set()
            else:
                print(f"Unhandled tdi_rsp_code {tdi_rsp_code}")
        else:
            print(f"unhandled rsp_code: {rsp_code}")

async def get_tile_id(device):
    for attempt in range(2):
        try:
            print(f"Connecting to Tile @ {device.address} - Attempt {attempt + 1}...")
            async with BleakClient(device.address, timeout=30) as client:
                tile_id_wrapper = Tile_ID_Wrapper(asyncio.Event())
                await client.start_notify(TILE_TOA_RSP_UUID, partial(tile_id_rsp_handler, tile_id_wrapper))
                await client.write_gatt_char(TILE_TOA_CMD_UUID, data)
                await tile_id_wrapper.got_tile_id_evt.wait()
                return tile_id_wrapper.tile_id
        except Exception as e:
            pass
    return "too_many_retries"

def empty_queue(q: asyncio.Queue):
    for _ in range(q.qsize()):
        q.get_nowait()
        q.task_done()
    print("Queue cleared")

async def connector(pq):
    # wait some time before connecting to make sure that we don't try to talk to the weaker connections first
    await asyncio.sleep(10)
    global scanning
    global search_id
    global found_tile_id
    while True: 
        print("connector looping")
        if (search_id is not None and found_tile_id) or (not scanning and pq.empty()):
            print("stopping connector")
            return
        # pull device off the queue
        device = (await pq.get())[1]
        tile_id = ""
        # Determine whether Tile is in range
        if int(device.rssi) > RSSI_Threshold.MODERATE.value:
            # if in range, get the Tile ID
            result = await get_tile_id(device)
            if result == "too_many_retries" :
                tile_id = pad("(Error: Too many retries)", Pad_Lengths.TILE_ID.value)
            elif result.upper() == search_id.upper():
                # tile of interest found
                found_tile_id = True
                # empty_queue(pq)
                tile_id = result.upper()
                print(await get_device_data(pq, device, None, tile_id))
                print("Tile of Interest Found")
            elif result.upper() != search_id.upper() and search_id is not None:
                print("Tile ID did not match")
            else:
                tile_id = pad(str(result).upper(), Pad_Lengths.TILE_ID.value)
        else:
            tile_id = pad("(Weak connection -- Bring the Tile closer to read Tile ID)", Pad_Lengths.TILE_ID.value)
        if search_id is None:
            print(await get_device_data(pq, device, None, tile_id))

async def main(id = None):
    time = 80.0
    args = sys.argv[1:]
    global search_id
    global tiles_found
    global scanning
    if len(args) == 0:
        print(f"{Formatting.INVERTED.value} Searching for all nearby Tile devices... {Formatting.CLEAR.value}")
    elif len(args) == 1:
        # if running in API:
        #search_id = id
        # if running in main:
        search_id = str(args[0])        
        print(f"{Formatting.INVERTED.value} Searching for Tile device with ID {search_id}... {Formatting.CLEAR.value}")
    print_header()
    # make the priority queue
    pq = asyncio.PriorityQueue()
    # set up the connector task
    connector_future = asyncio.create_task(connector(pq))
    # register the scanner and callback function
    scanner = BleakScanner()
    scanner.register_detection_callback(partial(detection_callback, pq))
    # run scanner
    await scanner.start()
    # TODO: clean this up
    # better way to do this: https://stackoverflow.com/questions/37209864/interrupt-all-asyncio-sleep-currently-executing
    time_slept = 0
    while (search_id is not None and not found_tile_id) or (time_slept < time):
        await asyncio.sleep(1)
        time_slept += 1
    print("stopping scanner")
    await scanner.stop()
    scanning = False
    # wait for the connector task to end before closing
    await connector_future

# TODO: finish search mode for a particular Tile ID

# Run the program, catching any interrupts
try: 
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nTiles found:", str(tiles_found), "(scanner terminated early)")
    sys.exit(0)