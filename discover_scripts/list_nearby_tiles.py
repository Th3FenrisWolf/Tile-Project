import asyncio
from bleak import BleakScanner, BleakClient
from enum import Enum
import sys, os
from functools import partial

sys.path.append(os.path.join(os.path.dirname(__file__), '../tile_api'))
from commands.tdi import Tdi_Cmd_Code, Tdi_Rsp_Code
from toa import Toa_Cmd_Code, Toa_Rsp_Code

# usage:
# python3 findTiles.py [search time] [address]
# 
# This script discovers and prints all nearby Tile Devices.
# to find all nearby (defaults to 60 second scan):
#   python3 findTiles.py
# to find all nearby for 2 minutes:
#   python3 findTiles 120
# to find specifically the Tile with address E6:9E:55:1A:91:28:
#   python3 findTiles 60 E6:9E:55:1A:91:28

known_devices = {
    # Change this dictionary to your own devices and known MAC addresses as you find them
    "Spare key":            "E6:9E:55:1A:91:28",
    "Wallet":               "DF:30:61:4F:AB:DA",
    "Backpack":             "E1:5B:A3:01:A0:F1",
    "Toy":                  "D1:7F:8E:E6:9E:B1",
    "madelines_earbud1":    "12:34:56:00:33:E1",
    "madelines_earbud2":    "12:34:56:00:37:1D"
}

found_addr_list = []
search_addr = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"
tiles_found = 0

# stuff used for getting the Tile ID
TILE_TOA_CMD_UUID = "9d410018-35d6-f4dd-ba60-e7bd8dc491c0"
TILE_TOA_RSP_UUID = "9d410019-35d6-f4dd-ba60-e7bd8dc491c0"
token = b"\x00" * 4
TOA_CONNECTIONLESS_CID = b"\x00"
data: bytes = TOA_CONNECTIONLESS_CID + token + Toa_Cmd_Code.TDI.value + Tdi_Cmd_Code.tile_id.value

# Label things true or false depending on what information you want to see:
class Display_Attributes(Enum):
    DEVICE_NUM = True
    NAME = True
    ADDRESS = True
    METADATA = False  # a lot of redundant information
    RSSI = True  # recommended to leave on
    INTERPRET_RSSI = True  # - displays connection strength - RSSI must be on to work
    UUIDS = False
    ADVERTISEMENT_DATA = False
    TILE_ID = False

class Pad_Lengths(Enum):
    DEVICE_NUM = 4
    NAME = 20   # <-- increase this value if you have longer known_device names
    RSSI = 3
    INTERPRET_RSSI = 22
    TILE_ID = 53

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
    head = "\u001b[7m"
    if Display_Attributes.DEVICE_NUM.value == True:
        head += pad("#", Pad_Lengths.DEVICE_NUM.value)
    if Display_Attributes.NAME.value == True:
        head += pad("Name", Pad_Lengths.NAME.value)
    if Display_Attributes.ADDRESS.value == True:
        head += pad("Address", 19)
    if Display_Attributes.INTERPRET_RSSI.value == True and Display_Attributes.RSSI.value == True:
        # we have to subtract some because of the alignment with the numbers below
        head += pad("Signal Strength", Pad_Lengths.INTERPRET_RSSI.value - 5)
    elif Display_Attributes.RSSI.value == True:
        head += pad("RSSI:", Pad_Lengths.RSSI.value)
    if Display_Attributes.METADATA.value == True:
        head += "Metadata:" + (" " * 20)
    if Display_Attributes.UUIDS.value == True:
        head += "UUID(s):" + (" " * 34)
    if Display_Attributes.ADVERTISEMENT_DATA.value == True:
        head += "Advertisement Data:" + (" " * 20)
    if Display_Attributes.TILE_ID.value == True:
        head += pad("Tile ID:", Pad_Lengths.TILE_ID.value)
    print(head + "\u001b[0m")

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

async def get_tile_id(btaddr):
    while True:
        try:
            print(f"trying to talk to bluetooth address {btaddr}")
            async with BleakClient(btaddr, timeout=20) as client:
                tile_id_wrapper = Tile_ID_Wrapper(asyncio.Event())
                await client.start_notify(TILE_TOA_RSP_UUID, partial(tile_id_rsp_handler, tile_id_wrapper))
                await client.write_gatt_char(TILE_TOA_CMD_UUID, data)
                await tile_id_wrapper.got_tile_id_evt.wait()
                #print("Tile ID: ", str(tile_id_wrapper.tile_id))
                return tile_id_wrapper.tile_id
        except Exception as e:
            pass

async def get_device_data(device, advertisement_data) -> str:
    info = ""
    if Display_Attributes.DEVICE_NUM.value == True:
        info += pad(str(tiles_found), Pad_Lengths.DEVICE_NUM.value)
    if Display_Attributes.NAME.value == True:
        info += pad(device.name, Pad_Lengths.NAME.value)
    if Display_Attributes.ADDRESS.value == True:
        info += device.address + "  "
    if Display_Attributes.RSSI.value == True:
        info += str(device.rssi) + " "
        if Display_Attributes.INTERPRET_RSSI.value == True:
            if int(device.rssi) > -50:
                info += pad("\u001b[32mStrong\u001b[0m", Pad_Lengths.INTERPRET_RSSI.value)
            elif int(device.rssi) > -70:
                info += pad("\u001b[33mModerate\u001b[0m", Pad_Lengths.INTERPRET_RSSI.value)
            elif int(device.rssi) < -69:
                info += pad("\u001b[31mWeak\u001b[0m", Pad_Lengths.INTERPRET_RSSI.value)
    # fix null metadata on Linux machines...
    if device.metadata:
        if Display_Attributes.METADATA.value == True:
            info += str(device.metadata) + "  "
        if Display_Attributes.UUIDS.value == True:
            info += str(device.metadata["uuids"]) + "  "
    if Display_Attributes.ADVERTISEMENT_DATA.value == True:
        info += str(advertisement_data)
    if Display_Attributes.TILE_ID.value == True:
        # get TDI information
        #print("getting tile ID")
        if int(device.rssi) > -70:
            tile_id = pad(await get_tile_id(device.address), Pad_Lengths.TILE_ID.value)
        else:
            tile_id = pad("(Too far away. Bring the Tile closer to read Tile ID)", Pad_Lengths.TILE_ID.value)
        info += tile_id
    return info

async def detection_callback(device, advertisement_data):
    # Whenever a device is found...
    global search_addr
    global found_addr_list
    global tileUUID
    global known_devices
    global tiles_found
    if tileUUID in device.metadata["uuids"]:
        # we found a tile
        if search_addr == None:
            # if not searching for any particular tile:
            # exclude devices we don't want to appear
            if device.address not in found_addr_list:
                # document only unique instances
                tiles_found += 1
                found_addr_list.append(device.address)
                # if device is known, give it a meaningful name
                if device.address in known_devices.values():
                    device.name = get_key(device.address, known_devices)
                    print(await get_device_data(device, advertisement_data))
                # otherwise just print
                else:
                    device.name = "Unknown Tile"
                    print(await get_device_data(device, advertisement_data))
        elif device.address == search_addr:
            # set name to friendly name if known
            if device.address in known_devices.values():
                device.name = get_key(device.address, known_devices)
            print("\u001b[1m----- Tile of interest found! -----\n", await get_device_data(device, advertisement_data))
            # since we found what we're looking for, exit
            sys.exit(0)

async def main(addr = None, time = 60.0):
    args = sys.argv[1:]
    global search_addr
    global tiles_found
    if len(args) == 0:
        print("\u001b[1mSearching for all Tile devices for", time, "seconds...\u001b[0m")
        print_header()
    elif len(args) == 1:
        time = float(args[0])
        print("\u001b[1mSearching for all Tile devices for", time, "seconds...\u001b[0m")
        print_header()
    elif len(args) == 2:
        time = float(args[0])
        addr = str(args[1])
        search_addr = addr.upper()
        print("\u001b[1mSearching for Tile w/ address", search_addr, "for", time, "seconds...\u001b[0m")  
        print_header()
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()
    print("\nTiles found:", str(tiles_found))

# Run the program, catching any ^Cs
try: 
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nTiles found:", str(tiles_found), "(scanner terminated early)")
    sys.exit(0)