import asyncio
from bleak import BleakScanner
from enum import Enum
import sys

# usage:
# python3 findTiles.py [search time] [address]
# 
# This script discovers and prints all nearby Tile Devices.

known_devices = {
    "Spare key":    "E6:9E:55:1A:91:28",
    "wallet":       "DF:30:61:4F:AB:DA",
    "backpack":     "E1:5B:A3:01:A0:F1",
    "toy":          "D1:7F:8E:E6:9E:B1"
}
excluded_devices = {
    "madelines_earbud1": "12:34:56:00:33:E1", 
    "madelines_earbud2": "12:34:56:00:37:1D"
}

found_addr_list = []
search_addr = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"
tiles_found = 0

# Label things true or false depending on what information you want to see:
class Display_Attributes(Enum):
    NAME = False # tiles generally don't have names, only 3rd party tile-equipped devices
    ADDRESS = True
    METADATA = False # a lot of redundant information
    RSSI = True
    INTERPRET_RSSI = True # - displays connection strength
    UUIDS = False
    ADVERTISEMENT_DATA = False

# function to return key for any value
def get_key(val, dict) -> str:
    for key, value in dict.items():
        if val == value:
            return key
    return "no key found"

def get_device_data(device, advertisement_data) -> str:
    info = ""
    if Display_Attributes.NAME.value == True:
        info += ("Name: " + str(device.name) + " ")
    if Display_Attributes.ADDRESS.value == True:
        info += ("Address: " + str(device.address) + " ")
    if Display_Attributes.RSSI.value == True:
        info += ("RSSI: " + str(device.rssi) + " ")
        if Display_Attributes.INTERPRET_RSSI.value == True:
            if int(device.rssi) > -50:
                info += "(Strong Connection) "
            elif int(device.rssi) > -70:
                info += "(Moderate Connection) "
            elif int(device.rssi) < -69:
                info += "(Weak connection) "
    # fix null metadata on Linux machines...
    if device.metadata:
        if Display_Attributes.METADATA.value == True:
            info += ("Metadata: " + str(device.metadata) + " ")
        if Display_Attributes.UUIDS.value == True:
            info += ("UUID(s): " + str(device.metadata["uuids"]) + " ")
    if Display_Attributes.ADVERTISEMENT_DATA.value == True:
        info += (str(advertisement_data))
    return info

def detection_callback(device, advertisement_data):
    # Whenever a device is found...
    global search_addr
    global found_addr_list
    global tileUUID
    global excluded_devices
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
                # if device is excluded...
                if device.address in excluded_devices.values:
                    device_name = excluded_devices[get_key(device.address, known_devices)]
                    print("excluded device found (" + str(device_name) + ")")
                # if device is known...
                elif device.address in known_devices.values():
                    device_name = known_devices[get_key(device.address, known_devices)]
                    print("Found known device --<<", str(device_name), ">>--", get_device_data(device, advertisement_data))
                # otherwise just print
                else:
                    print("Found unknown Tile (or Tile-equipped device) --", get_device_data(device, advertisement_data))
        elif device.address == search_addr:
            print("Tile of interest found! --", get_device_data(device, advertisement_data))
            # since we found what we're looking for, exit
            sys.exit(0)

async def main(addr = None, time = 60.0):
    args = sys.argv[1:]
    global search_addr
    global tiles_found
    if len(args) == 0:
        print("Searching for all Tile devices for", time, "seconds...")
    elif len(args) == 1:
        time = float(args[0])
        print("Searching for all Tile devices for", time, "seconds...")
    elif len(args) == 2:
        time = float(args[0])
        addr = str(args[1])
        search_addr = addr
        print("Searching for Tile w/ address", search_addr, "for", time, "seconds...")    
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()
    print("Tiles found:", str(tiles_found))

asyncio.run(main())